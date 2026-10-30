# AmbieGen (Topic 4) — minute-by-minute demo script

Companion to `demo-run.md` (the verified runbook), `deck.pptx` (20 slides) and
`research.md`. Talk format: **2 students × 10 minutes**; all demo action sits in
**Part 2 (Presenter 2), minutes 10:00–17:00**. Every run command below is copied
**verbatim from `demo-run.md`**; every expected number is copied from the actual
logs in `evidence/` (measured on this machine, 2026-10-16).

---

## 0. Pre-talk checklist (T−10 min, at the demo laptop)

| # | Check | How |
|---|-------|-----|
| 1 | Terminal open in the right folder | `cd tss\course-ambiegen` |
| 2 | venv alive, correct pymoo pin (must print `0.6.0`) | `.venv\Scripts\python.exe -c "import pymoo; print(pymoo.__version__)"` |
| 3 | Fallback images pre-open in Explorer | folder `evidence\builtin\16-10-2026_tc_images_nsga2\run0` |
| 4 | Deck open at slide 14 (Demo A pointer) | `deck.pptx` |

If the venv is broken, rebuild it once with the runbook's own setup block
(`demo-run.md` §0, ~2 min — do this **before** the talk, never live):

```bat
cd tss\course-ambiegen
git clone https://github.com/swat-lab-optimization/AmbieGen-tool AmbieGen-tool
python -m venv .venv
.venv\Scripts\python.exe -m pip install pymoo==0.6.0 shapely pandas numpy scipy matplotlib descartes
```

> Why the custom install line and not `requirements.txt`: the pinned
> `Shapely==1.8.4` does not build on Python 3.14, and `requirements.txt` omits
> `scipy`/`matplotlib`/`descartes`. `pymoo==0.6.0` is mandatory — 0.6.1+ stops
> passing the `algorithm` kwarg into `_evaluate` and crashes the repo
> (`KeyError: 'algorithm'`, `ambiegen/problems/robot_problem.py:23`). All
> verified in this session (`demo-run.md` §0).

---

## 1. Minute-by-minute (Part 2, Presenter 2)

| Clock | Slide | What happens |
|-------|-------|--------------|
| 10:00 | 12–13 | Part 2 divider + paper results (9 vs 2 robot failures, 14 vs 9 LKAS) |
| 10:45 | 14 | Show the robot-run slide, set up Demo A |
| **11:00** | **14** | **DEMO A launches (live, ~86 s)** |
| 12:45 | 14 | Talk over the finished convergence table; open the maze PNGs |
| 13:30 | 15 | Team case study: "Mountain Pass" config diff |
| **15:00** | **16** | **DEMO B launches (live, ~6 s)** |
| 15:15 | 16 | Open the road PNGs + point at the 4.65-vs-6 result |
| 16:00 | 17–18 | Strengths & limits, conclusions |
| 17:30 | 19–20 | References, then demo pointers / commands recap, thank-you, Q&A (buffer to 20:00) |

### 11:00 — DEMO A · built-in robot case study (~86 s measured)

Type exactly (from `demo-run.md` §1):

```bat
cd tss\course-ambiegen
.venv\Scripts\python.exe runners\run_builtin_robot.py
```

**While it runs (~86 s, 300 evaluations) — narrate the scrolling pymoo table:**

- Point at the `cv_min` column: it drops **52.99 → 17.92** over 15 generations —
  "constraint violation shrinking = the A* path length is climbing toward the
  150 failure bar."
- One-liner on what runs underneath: NSGA-II, population 20, 15 generations,
  seed 42, test suite of 5 (bounded demo budget; shipped defaults are 100 × 100).

**Expected final lines** (compare live output against `evidence/builtin/run_log.txt`):

```
The highest fitness found: 132.083261
Average diversity: 0.436659
[run_builtin_robot] total wall time: 85.5s
```

**Then open the money shot** (viewer command — convenience, not part of
demo-run.md):

```bat
start evidence\builtin\16-10-2026_tc_images_nsga2\run0\0.png
```

Say: "each image is one generated maze — the walls plus the A* path the robot is
forced to take; the title is that test's fitness, the A* path length
(132.1 / 126.9 / 126.9 / 121.3 / 120.7; a maze counts as fault-revealing above
150, `ambiegen/problems/robot_problem.py:43`)."

### 15:00 — DEMO B · team case study "Mountain Pass" (~6 s measured)

Type exactly (from `demo-run.md` §2):

```bat
.venv\Scripts\python.exe runners\run_team_vehicle.py
```

**It finishes in ~6 s — expected final lines** (from `evidence/team/run_log.txt`):

```
The highest fitness found: 4.648772
Average diversity: 0.582946
[team] images saved in 16-10-2026_team_tc_images_nsga2
[run_team_vehicle] total wall time: 5.9s
```

**Narrate:** "same search, our scenario — `cv_min` fell 2.357 → 1.351: the search
pushed the car's max lane deviation up toward our stricter failure bar of 6 every
generation, peaking at 4.649 without crossing it in this small budget."

**Then open a road image** (convenience viewer command):

```bat
start evidence\team\16-10-2026_team_tc_images_nsga2\run0\0.png
```

Say: "gray band = the road polygon on a 200×200 map; blue dots = the car's path
drifting off the centreline through the hairpins." Optionally also show the
scenario diff:

```bat
start evidence\team\team_scenario_config.json
```

---

## 2. Fallback plans (decide by 11:00 at the latest)

| Failure | Fallback |
|---------|----------|
| Demo A crashes or hangs (>2 min) | kill it, say "this is the pinned-deps fragility from the limits slide", open `evidence\builtin\run_log.txt` + the PNGs; continue with Demo B |
| Both live runs fail | Walk the two convergence tables in `evidence/*/run_log.txt` and the PNG suites; the numbers on slides 14/16 come from exactly those files |
| Running >40 s over schedule | Skip live Demo A (it is the long one); keep Demo B (6 s) — slide 14 already embeds two real maze images and the convergence chart |
| Terminal font too small for the room | Zoom with `Ctrl` + mouse wheel in Windows Terminal before the talk |

## 3. Optional longer demo (only if asked in Q&A; NOT run before)

The repo's own CLI at full defaults — ~33× the evaluations of Demo A, roughly
45–50 min extrapolated from the measured 85.5 s (**estimate, not measured** —
`demo-run.md` §3):

```bat
.venv\Scripts\python.exe optimize.py --problem robot --algorithm nsga2 --runs 1 --seed 42
```
