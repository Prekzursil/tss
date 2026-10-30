# AmbieGen — live demo runbook

Everything below was executed and timed on this machine (Windows, Python 3.14.6)
on 2026-10-16. Layout: work inside `tss/course-ambiegen/`, which contains
`AmbieGen-tool/` (the clone), `.venv/`, `runners/` (the two driver scripts) and
`evidence/` (saved outputs).

## 0. Clean clone + environment (one-time, ~2 min)

```bat
cd tss\course-ambiegen
git clone https://github.com/swat-lab-optimization/AmbieGen-tool AmbieGen-tool
python -m venv .venv
.venv\Scripts\python.exe -m pip install pymoo==0.6.0 shapely pandas numpy scipy matplotlib descartes
```

Resulting versions on this machine: `pymoo 0.6.0, shapely 2.2.0, pandas 3.0.6,
numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, descartes 1.1.0`.

Why not `pip install -r AmbieGen-tool\requirements.txt`: the pinned
`Shapely==1.8.4` has no wheel and does not build on Python 3.14 —
`ERROR: Failed to build 'Shapely'` / `AttributeError: module 'pkgutil' has no
attribute 'ImpImporter'` (exact output captured in this session). The
oldest-compatible pin that matters is **`pymoo==0.6.0`**: it is the
requirements.txt pin AND pymoo 0.6.1+ stops passing the `algorithm` kwarg into
`_evaluate`, which crashes the repo at `ambiegen/problems/robot_problem.py:23`
(`KeyError: 'algorithm'`).

## 1. Demo A — built-in case study: robot maze + NSGA-II (~90 s)

```bat
cd tss\course-ambiegen
.venv\Scripts\python.exe runners\run_builtin_robot.py
```

- What it does: runs the repo's own `optimize.main()` for the **robot** problem
  with **NSGA-II**, 1 run, seed 42, bounded budget pop 20 × 15 generations
  (defaults are 100 × 100, `AmbieGen-tool/config.py:2`), test suite of 5.
- Measured runtime: **85.5 s** wall clock (300 evaluations).
- What appears live: the pymoo convergence table scrolling in the terminal —
  point at the `cv_min` column dropping 52.99 → 17.92 (constraint violation
  shrinking = A* path length approaching the 150 failure threshold).
- What to open afterwards (copies already saved under `evidence\builtin\`):
  - `evidence\builtin\16-10-2026_tc_images_nsga2\run0\*.png` — **the money
    shot**: 5 generated maze scenarios (walls + planned robot path), title shows
    each test's fitness = A* path length 132.1 / 126.9 / 126.9 / 121.3 / 120.7
    (a maze is "fault-revealing" when the path exceeds 150,
    `ambiegen/problems/robot_problem.py:43`).
  - `evidence\builtin\16-10-2026_stats_nsga2\16-10-2026-stats.json` — suite
    fitness list + novelty 0.437.
  - `evidence\builtin\run_log.txt` — full log incl. convergence table.

## 2. Demo B — TEAM case study: "Mountain Pass" for the LKAS vehicle (~10 s)

```bat
cd tss\course-ambiegen
.venv\Scripts\python.exe runners\run_team_vehicle.py
```

- What it does: same search (NSGA-II, seed 42, pop 20 × 15 gens) but on our
  team-configured scenario: `max_len` 30→12, `min_angle` 10→25 (hairpin-like
  mountain road) and a stricter failure threshold of lane deviation > 6
  (builtin: 5). Config diff saved in
  `evidence\team\team_scenario_config.json`; explanation in
  `evidence\team\README.md`.
- Measured runtime: **5.9 s**.
- What appears live: convergence table, `cv_min` 2.357 → 1.351 — narrate it as
  "the search pushes the car's max lane deviation up toward the failure bar".
- What to open afterwards:
  - `evidence\team\16-10-2026_team_tc_images_nsga2\run0\*.png` — winding gray
    mountain roads with the car's path (blue dots) drifting off the
    centerline; titles show max deviation 4.65 / 4.38 / ... vs the 6 bar.
  - `evidence\team\team_scenario_config.json` — the scenario diff vs shipped
    defaults (good for one slide).
  - `evidence\team\16-10-2026_team_stats_nsga2\16-10-2026-stats.json` — suite
    fitness + novelty 0.583.

## 3. Talking points / gotchas (verified this session)

- Repo README's CLI example uses `--algo`; the real flag is `--algorithm`
  (`AmbieGen-tool/optimize.py:58`). `--problem {vehicle,robot}`,
  `--algorithm {nsga2,ga,random}`, `--runs`, `--seed` all work.
- `requirements.txt` omits `scipy`, `matplotlib`, `descartes` although the code
  imports them — the install line above includes them.
- Vehicle road images via the repo's own renderer crash in this environment
  (`descartes/patch.py:63 IndexError` with shapely ≥ 2), which is why the team
  driver rebinds image saving to a pure-matplotlib renderer. Robot images are
  unaffected (no descartes). On Python ≤ 3.11 the fully pinned
  `requirements.txt` route (Shapely 1.8.4 + descartes) should render vehicle
  images natively — **not verified here** (no ≤3.11 interpreter on this
  machine).
- Optional, longer demo (not run here): the repo's own CLI at full defaults —
  `.venv\Scripts\python.exe optimize.py --problem robot --algorithm nsga2
  --runs 1 --seed 42` — is 100 pop × 100 gens ≈ 33× the evaluations of Demo A;
  extrapolating from the measured 85.5 s that is roughly 45–50 min (estimate,
  not measured).
