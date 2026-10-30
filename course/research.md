# AmbieGen — Research Knowledge Base (Course Topic 4)

Course topic: "Automatic Search-based Test Case Generation for Autonomous Systems cu AmbieGen"
Sources verified in this session:
- **Paper**: arXiv 2301.01234 — "AmbieGen: A Search-based Framework for Autonomous Systems Testing", Dmytro Humeniuk, Foutse Khomh, Giuliano Antoniol (abs page + full HTML fetched 2026-10-16). Published version: *Science of Computer Programming*, vol. 230, article 102990, 2023, doi 10.1016/j.scico.2023.102990 (citation block in `AmbieGen-tool/README.md`).
- **Repo**: github.com/swat-lab-optimization/AmbieGen-tool — cloned locally at `C:\Users\Prekzursil\.zcode\workspace\default\AmbieGen-tool` (`git clone --depth 1`, 2026-10-16) and **executed** (see §7 for receipts).

Citation convention: `[paper §X]` = arXiv HTML section; `path:line` = local clone of the repo.

---

## 1. What AmbieGen is

A **search-based framework for automatic test generation for autonomous systems** [paper Abstract]. Testing is *model-in-the-loop*: scenarios are simulated against (simplified) models of the system under test because the parameter space is too large for exhaustive simulation; evolutionary search is used to "identify the most critical scenarios" [paper Abstract]. The design is modular — new systems under test, algorithms, and search operators can be added [paper Abstract; README "Adding a new problem"]. In the repo it appears as **version 0.1.0**, MIT-licensed (README header badge + "License" section).

Paper's experiment systems under test [paper case-study sections]:
- **Robot**: a Pioneer 3-AT robot with a SICK LMS200 laser (10 m range) using a nearness-diagram obstacle-avoidance navigation, simulated in **Player/Stage**.
- **Vehicle**: a **Lane Keeping Assist System (LKAS)** tested in the **BeamNG.tech** simulator; failure criterion = more than **85% of the car's area leaving the lane**; speed capped at 70 km/h.

⚠️ **No "smart home" case study exists** — the phrase does not appear anywhere in the paper (checked explicitly via fetch) and the repo contains only `robot` and `vehicle` problems (`ambiegen/problems/`, `--problem` help text in `optimize.py:57`). Any course case study beyond these two must be **created by the team** (see §6).

## 2. Search algorithm (exact)

Three algorithms, all built on the **Pymoo framework** [paper; README "Options and parameters"]:

| Key | Algorithm | Objectives |
|---|---|---|
| `ga` | single-objective genetic algorithm | 1: fault-revealing fitness |
| `nsga2` | **NSGA-II** (multi-objective GA) | 2: fitness + diversity/novelty |
| `random` | random search (baseline) | — |

Code registry: `ambiegen/__init__.py:1-9` maps `"ga"`→`pymoo...nonconvex.ga.GA`, `"nsga2"`→`pymoo...moo.nsga2.NSGA2`, `"random"`→`pymoo...soo.nonconvex.random_search.RandomSearch`. The algorithm is instantiated in `optimize.py:86-94` with problem-specific sampling/crossover/mutation and duplicate elimination; `pymoo.optimize.minimize` runs it (`optimize.py:112-120`).

Operators [paper; verified in code]:
- **Crossover**: one-point crossover over the state lists, applied with probability `cross_rate` (0.9) — `ambiegen/search_operators/robot_crossover.py:31-50` (random cut point, swap tails).
- **Mutation** (probability `mut_rate` = 0.4, 1–3 repetitions): either **exchange** (swap two random environmental elements) or **change of variable** (re-roll one element's type + regenerate its length/angle) — `ambiegen/search_operators/vehicle_mutation.py:23-77`.
- **Sampling**: random valid initial population — e.g. roads grown from random straight/right/left actions until the map border is hit, then validity-checked (`ambiegen/samplers/vehicle_sampling.py:22-56`).

Config defaults (shipped `config.py:2`): `ga = {"pop_size": 100, "n_gen": 100, "mut_rate": 0.4, "cross_rate": 0.9, "test_suite_size": 10}`. Note the README's illustrative snippet shows 150/200/30 — the paper's example config also used pop 150 × 200 gens [paper]; the *shipped* file uses 100×100 and suite 10.

## 3. Fitness functions (from paper + code)

Both fitnesses are **negative values minimized by pymoo** (so the search maximizes the underlying quantity), computed on a **simplified model** of the SUT, not on the full simulator [paper].

- **Vehicle (LKAS)**: the paper defines fitness by the *biggest deviation from the lane center* (maximize). In code (`ambiegen/solutions/vehicle_solution.py:36-61` → `evaluate_scenario`, `ambiegen/utils/vehicle_evaluate.py:99-163`): the road points are spline-interpolated; a `KinematicModel` (kinematic bicycle-style update: `x += speed·cos(yaw)·dt`, `yaw += steering·dt` — `ambiegen/utils/kinematic_model.py`) driven by a waypoint-following `LaneController` (`ambiegen/utils/lane_controller.py`) simulates the car at each step; fitness = **−max over time of the distance between the car and the nearest road (centerline) waypoint** (`vehicle_evaluate.py:154-157`); if the car path self-intersects, per-step distances are capped at 3 (`vehicle_evaluate.py:148-151`); invalid roads get fitness 0. Constraint `G = 5 − |fitness|` requires max deviation > 5 (`ambiegen/problems/vehicle_problem.py:24,64`).
- **Robot**: the paper defines fitness by the *length of the path to reach the goal* (maximize → harder mazes). In code (`ambiegen/solutions/robot_solution.py:34-58`): the obstacle map is built from states, an **A\* planner** (`ambiegen/utils/a_star.py`) plans from (1,1) to (map_size−2, map_size−2); fitness = **−(A\* path length)** (`robot_solution.py:52-56`). Constraint `G = 150 − path_length` requires the path to exceed 150 (`ambiegen/problems/robot_problem.py:43,65`).
- **Diversity/novelty objective (2nd objective for NSGA-II)** [paper]: novelty of a scenario = average novelty vs the **5 solutions with the highest fault-revealing fitness** in the current population — implemented in `ambiegen/problems/vehicle_problem.py:49-61` and `robot_problem.py:24-39`. Pairwise novelty is Jaccard-distance-based: `novelty = 1 − |intersection| / (|tc1| + |tc2| − |intersection|)` where two elements "intersect" if they have the same type and near-equal parameters (≤5 for vehicle, ≤2 for robot) — `ambiegen/solutions/vehicle_solution.py:64-101`, `robot_solution.py:60-94`.

**Test-case encoding** [paper; README "Representation of the test cases"]: a test case is a list of environmental elements, each element = list of N attributes:
- robot: 3 attributes — obstacle type (0 horizontal / 1 vertical wall), size, x-position;
- vehicle: 3 attributes — segment type (0 straight / 1 turn right / 2 turn left), straight length, turning angle.
Variable-length solutions are supported (one-point crossover works across lengths).

**Outputs**: after the run, a test suite of `test_suite_size` scenarios is taken from the last generation (`ambiegen/utils/get_test_suite.py`), and per-run stats are saved: fitness list of the suite + average pairwise novelty of the suite (`ambiegen/utils/get_stats.py`) + convergence (best per generation). Files land in date-prefixed folders, e.g. `16-10-2026_stats_nsga2/`, `16-10-2026_tcs_nsga2/`, `16-10-2026_tc_images_nsga2/` (verified on disk after my runs; folder naming from `config.py:3` + algorithm suffix, README Usage §6).

## 4. Reported results (paper)

- Budget: **30 runs**, **2-hour time budget per run**; NSGA-II pop 150 × 200 gens vs random search [paper].
- **Robot**: "On average, AmbieGen detected **9 failures** in two hours, compared to **2 failures** for random search" [paper].
- **LKAS (BeamNG, SBST'22 pipeline)**: "AmbieGen and Frenetic on average produced almost the same number of failures (**14**), while Random Search produced an average of **9** failures" [paper]. AmbieGen is "the winner of SBST 2022 tool competition" (most diverse fault-revealing scenarios under a limited time budget) [paper].

## 5. Strengths and limits

**Strengths** (grounded in paper/repo):
- Modular extension to new SUTs via 4 small classes (README "Adding a new problem").
- Cheap fitness via simplified models → 2 h budget suffices for a 30-case suite [paper].
- Multi-objective diversity preservation (NSGA-II + novelty) → diverse fault-revealing suites; SBST'22 winner [paper].
- Deterministic-ish tooling: seeds (`--seed`), duplicate elimination (`optimize.py:92`), stats/boxplot comparison utilities (`compare.py`, `demo.py`).

**Limits** (paper's implicit limits + verified repo facts):
- Fitness uses simplified models, not the real simulator; scenario representation is limited to 2D attribute arrays (no pedestrians/traffic/other cars) [paper future-work discussion].
- Only 2 problems (robot, vehicle) and 3 algorithms in the tool; future work: quality-diversity search, surrogate/neuron-coverage/surprise-adequacy fitness, SCENIC representation, CARLA/LGSVL integration [paper].
- Adding a new problem requires implementing Problem + Sampling + Crossover/Mutation + Solution classes (README).
- Repo rough edges (verified): README CLI example uses `--algo` but the actual flag is **`--algorithm`** (`optimize.py:58`, confirmed by `--help`); README says default `runs=1` but code default is `runs=2` (`optimize.py:59`); `requirements.txt` omits `scipy`, `matplotlib`, `descartes` although the code imports them (`vehicle_evaluate.py:2,4,6`; `vehicle_solution.py:3-6`); pinned versions do not build on modern Python (see §7); the BeamNG pipeline code is commented out in the open-source repo (`vehicle_evaluate.py:12-13`), so the tool itself evaluates only with the simplified kinematic model.

## 6. Creating a team case study (course requirement)

The framework's intended extension path (README "Adding a new problem") — implement and register:
1. `YourProblem` (ElementwiseProblem; 1- or 2-objective + constraint) — pattern: `ambiegen/problems/robot_problem.py`;
2. `YourSampling` (initial population) — pattern: `ambiegen/samplers/`;
3. `YourCrossover` + `YourMutation` — pattern: `ambiegen/search_operators/`;
4. `YourSolution` with `eval_fitness()`, `intersect()`, `calculate_novelty()`, `build_image()` — pattern: `ambiegen/solutions/`.
Register in `ambiegen/problems/__init__.py`, `samplers/__init__.py`, `search_operators/__init__.py`, `solutions/__init__.py`, then run `python optimize.py --problem <name> --algorithm nsga2`. Environment constants (map size, min/max attribute values, output paths) go in `config.py` (`vehicle_env`/`robot_env`/`files` sections, `config.py:3-19`).

**Scope decision for our team case study (stated plainly).** The team case study
("Mountain Pass", `runners/run_team_vehicle.py`) is a **team-designed scenario
for the shipped LKAS SUT** — runtime reconfiguration of `vehicle_env` plus one
subclass tightening the failure threshold — **not a brand-new SUT built via the
4-class recipe above**. This was a deliberate scope choice for the bounded
session; the new-SUT path is fully mapped in this section and listed under "if
we had more time" on slide 18 of the deck. A strict reading of "implement a new
system under test" would require the 4-class route; our claim is the narrower
and explicitly labeled one: a new *scenario* (geometry + failure criterion)
for the built-in vehicle problem, with zero repo files modified.

## 7. How to run it locally (verified on Windows, 2026-10-16)

**Claimed by README**: Python 3.8+, `pip install -r requirements.txt`, then `python optimize.py` (one NSGA-II run for vehicle by default). Pinned deps (`requirements.txt:1-4`): `pymoo==0.6.0`, `Shapely==1.8.4`, `pandas==1.5.0`, `numpy==1.23.3`.

**What I actually ran** (Python 3.14.6, cmd/bash on Windows):
```
git clone https://github.com/swat-lab-optimization/AmbieGen-tool.git
python -m venv ambiegen-venv
ambiegen-venv/Scripts/python.exe -m pip install -r AmbieGen-tool/requirements.txt
  → FAILED: "ERROR: Failed to build 'Shapely'" (Shapely 1.8.4 has no wheel and does not build on 3.14)
ambiegen-venv/Scripts/python.exe -m pip install pymoo shapely pandas numpy scipy matplotlib descartes
  → pymoo 0.6.2, shapely 2.2.0, numpy 2.5.4, pandas 3.0.6
```
- **Robot smoke run** (pop 12, 5 gens, NSGA-II, seed 42, via a driver that patches `config.ga` at runtime — repo files untouched): with pymoo **0.6.2** it CRASHED (`KeyError: 'algorithm'` at `robot_problem.py:23` — 0.6.2 stopped passing the `algorithm` kwarg into `_evaluate`). After `pip install pymoo==0.6.0` it **PASSED**: convergence table printed (cv_min 70.3 → 53.2 over 5 gens) and outputs saved — `16-10-2026_stats_nsga2/16-10-2026-stats.json` (fitness + novelty 0.726), `16-10-2026_tcs_nsga2/16-10-2026-tcs.json`, `16-10-2026_tc_images_nsga2/`.
- **Vehicle smoke run** (same settings): optimization + stats + test-cases JSON saved fine (suite fitness ≈ 3.0–3.4 = max deviation from road centerline), but **image rendering crashed** (`IndexError` in `descartes/patch.py:63` — the unmaintained `descartes` package is incompatible with shapely ≥ 2, used at `vehicle_solution.py:142`). The robot problem's images do not use descartes and render fine.
- **CLI verified**: `python optimize.py --help` shows `--problem {vehicle,robot}`, `--algorithm {nsga2,ga,random}`, `--runs`, `--save_results`, `--seed`, `--debug` — the README's `--algo` example is wrong; use `--algorithm`. (Repo's own `demo.py` also uses `--algorithm`.)

**Recommended local setup** (combining README intent with my verification):
```
git clone https://github.com/swat-lab-optimization/AmbieGen-tool.git
cd AmbieGen-tool
python -m venv venv && venv\Scripts\activate        # use Python 3.8–3.11 for full pinned support
pip install -r requirements.txt                      # on ≤3.11 this installs Shapely 1.8.4 etc.
pip install scipy matplotlib descartes               # missing from requirements.txt but imported
python optimize.py --problem robot  --algorithm nsga2 --runs 1
python optimize.py --problem vehicle --algorithm nsga2 --runs 1
python compare.py --stats_path="DD-MM-YYYY_stats_nsga2" "DD-MM-YYYY_stats_random" --stats_names "NSGA-II" "Random"
```
Not run by me (stated as such): the fully pinned install on Python ≤3.11 — I could not build Shapely 1.8.4 on the only available interpreter (3.14.6). On Python 3.14 the working combination I verified is `pymoo==0.6.0` + latest `shapely/pandas/numpy/scipy/matplotlib/descartes`, accepting the vehicle image-rendering crash (stats/tcs still saved). `demo.py` (3 runs × {random, nsga2} for vehicle + compare) was not run — it uses the same verified code path.

## 8. Source index

- Paper abs: https://arxiv.org/abs/2301.01234 · full HTML: https://arxiv.org/html/2301.01234 (sections cited above)
- README.md sections: Installation, Usage, Options and parameters, Representation of the test cases, Adding a new problem, License
- Code (local clone `AmbieGen-tool/`): `optimize.py`, `config.py`, `compare.py`, `demo.py`, `requirements.txt`, `ambiegen/__init__.py`, `ambiegen/problems/{robot,vehicle}_problem.py`, `ambiegen/solutions/{robot,vehicle}_solution.py`, `ambiegen/samplers/*`, `ambiegen/search_operators/*`, `ambiegen/utils/{vehicle_evaluate,kinematic_model,lane_controller,a_star,get_stats,get_test_suite}.py`
