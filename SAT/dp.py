import sys
import time
import tracemalloc
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict


def parse(file_path: str) -> Tuple[int, List[List[int]]]:
    clauses: List[List[int]] = []
    num_vars = 0

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) != 4 or parts[1] != 'cnf':
                    raise ValueError(f"Invalid header: {line}")
                num_vars = int(parts[2])
                continue

            lits = list(map(int, line.split()))
            if lits and lits[-1] == 0:
                lits = lits[:-1]
            if lits:
                clauses.append(lits)

    return num_vars, clauses


def simplify_formula(clauses: List[List[int]], assignment: Dict[int, bool]) -> List[List[int]]:
    result = []

    for clause in clauses:
        new_clause = []
        is_satisfied = False

        for lit in clause:
            var = abs(lit)
            if var in assignment:
                if (lit > 0 and assignment[var]) or (lit < 0 and not assignment[var]):
                    is_satisfied = True
                    break
                continue
            else:
                new_clause.append(lit)

        if not is_satisfied:
            if not new_clause:
                return [[]]
            result.append(new_clause)

    return result


def unit_propagate(clauses: List[List[int]], assignment: Dict[int, bool]) -> Tuple[
    Dict[int, bool], List[List[int]], bool]:
    simplified = simplify_formula(clauses, assignment)

    if any(len(clause) == 0 for clause in simplified):
        return assignment, simplified, False

    while True:
        unit_clauses = [clause[0] for clause in simplified if len(clause) == 1]
        if not unit_clauses:
            break

        for lit in unit_clauses:
            var = abs(lit)
            val = lit > 0

            if var in assignment and assignment[var] != val:
                return assignment, [[]], False

            assignment[var] = val

        simplified = simplify_formula(clauses, assignment)

        if any(len(clause) == 0 for clause in simplified):
            return assignment, simplified, False

    return assignment, simplified, True

def find_pure_literals(clauses: List[List[int]]) -> Dict[int, bool]:
    pos_vars = set()
    neg_vars = set()

    for clause in clauses:
        for lit in clause:
            if lit > 0:
                pos_vars.add(abs(lit))
            else:
                neg_vars.add(abs(lit))

    pure_lits = {}

    for var in pos_vars - neg_vars:
        pure_lits[var] = True

    for var in neg_vars - pos_vars:
        pure_lits[var] = False

    return pure_lits

def compute_jeroslow_wang(clauses: List[List[int]]) -> Dict[int, float]:
    scores = defaultdict(float)

    for clause in clauses:
        weight = 2 ** -len(clause)
        for lit in clause:
            var = abs(lit)
            scores[var] += weight

    return scores


def select_variable(clauses: List[List[int]], assignment: Dict[int, bool]) -> Optional[int]:
    scores = compute_jeroslow_wang(clauses)

    best_var = None
    best_score = -1

    for var, score in scores.items():
        if var not in assignment and score > best_score:
            best_var = var
            best_score = score

    return best_var

def davis_putnam(clauses: List[List[int]], assignment: Dict[int, bool] = None) -> Optional[Dict[int, bool]]:
    if assignment is None:
        assignment = {}

    assignment, simplified, success = unit_propagate(clauses, assignment)
    if not success:
        return None

    if not simplified:
        return assignment

    pure_lits = find_pure_literals(simplified)
    if pure_lits:
        for var, val in pure_lits.items():
            assignment[var] = val
        return davis_putnam(clauses, assignment)

    var = select_variable(simplified, assignment)
    if var is None:
        return assignment

    assignment_copy = assignment.copy()
    assignment_copy[var] = True
    result = davis_putnam(clauses, assignment_copy)
    if result is not None:
        return result

    assignment[var] = False
    return davis_putnam(clauses, assignment)


def solve_sat(file_path: str) -> None:
    num_vars, clauses = parse(file_path)

    tracemalloc.start()
    start_time = time.time()

    result = davis_putnam(clauses)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result is None:
        print("UNSATISFIABLE")
    else:
        print("SATISFIABLE")
        for var in range(1, num_vars + 1):
            if var not in result:
                result[var] = False

        for var in sorted(result.keys()):
            print(f"{var} = {result[var]}")

    print(f"Runtime: {end_time - start_time:.4f} s")
    print(f"Peak memory usage: {peak / 1e6:.3f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dp_solver.py file.cnf")
        sys.exit(1)

    solve_sat(sys.argv[1])