import sys
import time
import tracemalloc

def parse(file):
    clauses = []
    num_vars = 0

    with open(file, 'r') as f:
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

    return clauses, num_vars

def find_unit_clause(clauses, assignment):
    for clause in clauses:
        unassigned = [l for l in clause if abs(l) not in assignment]
        if len(unassigned) == 1:
            return unassigned[0]
    return None

def find_pure_literal(clauses, assignment):
    counter = {}
    for clause in clauses:
        for lit in clause:
            if abs(lit) in assignment:
                continue
            counter[lit] = counter.get(lit, 0) + 1
    for lit in counter:
        if -lit not in counter:
            return lit
    return None

def simplify_clauses(clauses, lit):
    new_clauses = []
    for clause in clauses:
        if lit in clause:
            continue
        if -lit in clause:
            new_clause = [x for x in clause if x != -lit]
            if not new_clause:
                return None
            new_clauses.append(new_clause)
        else:
            new_clauses.append(clause)
    return new_clauses

def cdcl(clauses, assignment, num_vars):
    while True:
        unit = find_unit_clause(clauses, assignment)
        if unit is not None:
            assignment[abs(unit)] = (unit > 0)
            clauses = simplify_clauses(clauses, unit)
            if clauses is None:
                return None
            continue

        pure = find_pure_literal(clauses, assignment)
        if pure is not None:
            assignment[abs(pure)] = (pure > 0)
            clauses = simplify_clauses(clauses, pure)
            if clauses is None:
                return None
            continue
        break

    if not clauses:
        return assignment

    for clause in clauses:
        if not clause:
            return None

    for var in range(1, num_vars + 1):
        if var not in assignment:
            break
    else:
        return assignment

    for val in [True, False]:
        new_assign = assignment.copy()
        new_assign[var] = val
        new_clauses = simplify_clauses(clauses, var if val else -var)
        if new_clauses is not None:
            result = cdcl(new_clauses, new_assign, num_vars)
            if result is not None:
                return result

    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cdcl.py file.cnf")
        sys.exit(1)

    filename = sys.argv[1]
    clauses, num_vars = parse(filename)

    tracemalloc.start()
    start_time = time.time()

    result = cdcl(clauses, {}, num_vars)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result is None:
        print("UNSATISFIABLE")
    else:
        print("SATISFIABLE")
        for var in sorted(result):
            print(f"{var} = {result[var]}")

    print(f"Runtime: {end_time - start_time:.4f} s")
    print(f"Peak memory usage: {peak / 1e6:.3f} MB")
