# SAT-Solvers-for-MPI
The materials I used for my SAT solvers

Running the solvers is easy:
1) Open a solver from the bunch;
2) Open the terminal;
3) Type in: python solver_name.py cnf_name.py.

!WARNING! Not all SAT solvers output the same solutions. In the case of WalkSAT you may get multiple, different solutions. Keep in mind that they all work. Just because DPLL found another solution does not mean that WalkSAT is wrong. It just means it found another solution that can work.

!!WARNING!! Some SAT solvers (most of them) will take a long time to execute if they are imputed an UNSATISFIABLE CNF, the problem is not intentional but rather an error on my part. Treat with caution and do not wait them out. They will never end.

!!!WARNING!!! Big CNFs will mostly guaranteed take more than a few hours to complete. Do not expect to run a 1800 variable CNF with 200000 clauses and get an answer within 5 working days. These are more or less prototypes done by a Novice. Run the code at your own risks.
