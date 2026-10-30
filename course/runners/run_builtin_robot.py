"""
Built-in AmbieGen case study: ROBOT problem, NSGA-II, 1 run.

Runs the repo's own `optimize.main()` with a reduced budget (pop 20 x 15
generations, test suite of 5) so the run stays bounded on a laptop.
Repo files are NOT modified: `config.ga` is patched at runtime only.
"""
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AmbieGen-tool"))
sys.path.insert(0, REPO)
os.chdir(REPO)

import config as cf

# bounded budget (defaults are pop 100 x 100 gens, suite 10 - cf config.py:2)
cf.ga.update({"pop_size": 20, "n_gen": 15, "mut_rate": 0.4, "cross_rate": 0.9,
              "test_suite_size": 5})

import optimize


def main():
    t0 = time.time()
    optimize.main(problem="robot", algo="nsga2", runs_number=1,
                  save_results=True, random_seed=42, debug=False)
    print(f"\n[run_builtin_robot] total wall time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    # guard so an accidental `import run_builtin_robot` can no longer launch
    # the ~85 s optimization (the run itself is unchanged)
    main()
