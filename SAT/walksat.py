import random
import sys
import time
import tracemalloc

def parse(file):
    new_file = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p'):
                continue
            clause = line.split()
            if clause[-1] == '0':
                literal = [int(x) for x in clause[:-1]]
            else:
                literal = [int(x) for x in clause]
            if literal:
                new_file.append(literal)
    return new_file

def evaluate_clause(clause, assignment):
    return any((lit > 0 and assignment[abs(lit)]) or (lit < 0 and not assignment[abs(lit)]) for lit in clause)

def walksat(cnf, num_vars, max_flips=1000, p=0.5):
    assignment = {i + 1: random.choice([True, False]) for i in range(num_vars)}
    for _ in range(max_flips):
        unsatisfied = [c for c in cnf if not evaluate_clause(c, assignment)]
        if not unsatisfied:
            return assignment
        clause = random.choice(unsatisfied)
        if random.random() < p:
            var = abs(random.choice(clause))
        else:
            def score(v):
                assignment[v] = not assignment[v]
                count = sum(evaluate_clause(c, assignment) for c in cnf)
                assignment[v] = not assignment[v]
                return count
            var = max((abs(l) for l in clause), key=score)
        assignment[var] = not assignment[var]
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python walksat.py file.cnf")
        sys.exit(1)

    filename = sys.argv[1]
    cnf = parse(filename)

    num_vars = max(abs(lit) for clause in cnf for lit in clause)

    tracemalloc.start()
    start_time = time.time()

    ending = walksat(cnf, num_vars)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if ending is None:
        print("UNSATISFIABLE (or no solution found within max_flips)")
    else:
        print("SATISFIABLE")
        for var in sorted(ending):
            print(f"{var}: {ending[var]}")

    print("Runtime: {:.4f} seconds".format(end_time - start_time))
    print(f"Peak memory usage: {peak / 10**6:.3f} MB")