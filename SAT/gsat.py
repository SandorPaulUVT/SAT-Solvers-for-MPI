import sys
import time
import tracemalloc
import random

def parse_dimacs(file_path):
    clauses = []
    num_vars = 0
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) >= 4 and parts[1] == 'cnf':
                    num_vars = int(parts[2])
                continue
            lits = list(map(int, line.split()))
            if lits and lits[-1] == 0:
                lits = lits[:-1]
            if lits:
                clauses.append(lits)
                num_vars = max(num_vars, max(abs(l) for l in lits))
    return num_vars, clauses


def gsat(clauses, num_vars, max_tries=100, max_flips=10000, p_random=0.3):
    def num_satisfied(assignment):
        count = 0
        for clause in clauses:
            if any((l > 0 and assignment[abs(l)]) or (l < 0 and not assignment[abs(l)]) for l in clause):
                count += 1
        return count

    for _ in range(max_tries):
        assignment = {i: random.choice([True, False]) for i in range(1, num_vars+1)}
        best_sat = num_satisfied(assignment)
        if best_sat == len(clauses):
            return assignment

        for _ in range(max_flips):
            if random.random() < p_random:
                var = random.randint(1, num_vars)
            else:
                gains = []  # (gain, var)
                for var in range(1, num_vars+1):
                    assignment[var] = not assignment[var]
                    sat = num_satisfied(assignment)
                    gain = sat - best_sat
                    gains.append((gain, var, sat))
                    assignment[var] = not assignment[var]
                max_gain = max(g[0] for g in gains)
                best_vars = [var for gain, var, sat in gains if gain == max_gain]
                var = random.choice(best_vars)

            assignment[var] = not assignment[var]
            current_sat = num_satisfied(assignment)
            if current_sat > best_sat:
                best_sat = current_sat
            if best_sat == len(clauses):
                return assignment
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gsat_solver.py <cnf-file> [max_tries] [max_flips]")
        sys.exit(1)

    filename = sys.argv[1]
    max_tries = int(sys.argv[2]) if len(sys.argv) >= 3 else 100
    max_flips = int(sys.argv[3]) if len(sys.argv) >= 4 else 10000

    num_vars, clauses = parse_dimacs(filename)

    tracemalloc.start()
    start_time = time.time()

    result = gsat(clauses, num_vars, max_tries, max_flips)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result is None:
        print("UNSATISFIABLE (within limits)")
    else:
        print("SATISFIABLE")
        for v in sorted(result):
            print(f"{v} = {result[v]}")

    print(f"Runtime: {end_time - start_time:.4f} seconds")
    print(f"Peak memory usage: {peak / 10**6:.3f} MB")
