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

def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return clause[0]
    return None

def find_pure_literal(clauses):
    counts = {}
    for clause in clauses:
        for lit in clause:
            counts[lit] = counts.get(lit, 0) + 1
    for lit in counts:
        if -lit not in counts:
            return lit
    return None

def simplify_clauses(clauses, lit):
    new_clauses = []
    for clause in clauses:
        if lit in clause:
            continue  # Clause is satisfied
        if -lit in clause:
            new_clause = [x for x in clause if x != -lit]
            if not new_clause:
                return None  # Conflict (empty clause)
            new_clauses.append(new_clause)
        else:
            new_clauses.append(clause)
    return new_clauses

def dpll(clauses, assignment):

    while True:
        unit = find_unit_clause(clauses)
        if unit is None:
            break
        assignment[abs(unit)] = (unit > 0)
        clauses = simplify_clauses(clauses, unit)
        if clauses is None:
            return None

    while True:
        pure = find_pure_literal(clauses)
        if pure is None:
            break
        assignment[abs(pure)] = (pure > 0)
        clauses = [cl for cl in clauses if pure not in cl]

    if not clauses:
        return assignment
    for clause in clauses:
        if not clause:
            return None

    lit = clauses[0][0]
    var = abs(lit)

    # Branch 1: try literal = True
    new_assign = assignment.copy()
    new_assign[var] = (lit > 0)
    new_clauses = simplify_clauses(clauses, lit)
    if new_clauses is not None:
        result = dpll(new_clauses, new_assign)
        if result is not None:
            return result

    new_assign = assignment.copy()
    new_assign[var] = not (lit > 0)
    new_clauses = simplify_clauses(clauses, -lit)
    if new_clauses is not None:
        return dpll(new_clauses, new_assign)

    return None

if __name__ == "__main__":

    filename = sys.argv[1]
    cnf = parse(filename)

    tracemalloc.start()
    start_time = time.time()

    ending = dpll(cnf, {})

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if ending is None:
        print("UNSATISFIABLE")
    else:
        print("SATISFIABLE")
        for var in sorted(ending):
            print(f"{var}: {ending[var]}")

    print("Runtime: {:.4f} seconds".format(end_time - start_time))
    print(f"Peak memory usage: {peak / 10**6:.3f} MB")