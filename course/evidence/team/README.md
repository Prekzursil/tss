# Team case study: "Mountain Pass" — new scenario for the vehicle (LKAS) system

> **Scope note.** This is a team-designed *scenario* for the **shipped** LKAS
> system under test (runtime reconfiguration + one subclass), **not a
> brand-new SUT** — that 4-class extension path is mapped in `research.md` §6.
> The claim made for this case study is exactly the narrower one below.

**What is new in our scenario.** The shipped vehicle case study generates generic
roads on a 200x200 map where straight segments may be up to 30 units long and a
turning segment can rotate by as little as 10 degrees (`AmbieGen-tool/config.py:5-11`),
with a test counted as fault-revealing when the car's maximum deviation from the
lane centreline exceeds 5 (`ambiegen/problems/vehicle_problem.py:64`). Our team
scenario, **"Mountain Pass"**, re-configures the same supported system through the
repo's native scenario format (the `vehicle_env` dict) into a sustained-curvature
mountain road: straight segments are capped at 12 units (`max_len` 30 → 12) so the
lane-keeping controller never gets a long stable stretch to settle in, every turn
must rotate at least 25 degrees (`min_angle` 10 → 25) producing hairpin-like
sequences, and we tighten the team-defined failure criterion to a lane deviation
of more than 6 (subclass `MountainVehicleProblem2Obj`, threshold 5 → 6). The
research question the case study answers: *can the search still drive the simplified
LKAS model out of its lane when the road geometry is aggressively curvy and the
failure bar is higher?* In our bounded run (NSGA-II, pop 20 x 15 generations,
seed 42) the best scenario reached a maximum deviation of **4.649** (constraint
violation 1.351, monotonically reduced from 2.357 over the run) — the search
pushed deviation up 15 generations in a row but did not cross the stricter
threshold of 6 within this small budget, with a suite novelty of 0.583.

## Files

- `team_scenario_config.json` — the exact scenario configuration (diff vs shipped defaults included)
- `run_log.txt` — full stdout/log of the run, including the pymoo convergence table
- `16-10-2026_team_stats_nsga2/16-10-2026-stats.json` — suite fitness + novelty
- `16-10-2026_team_stats_nsga2/16-10-2026-conv.json` — convergence data
- `16-10-2026_team_tcs_nsga2/16-10-2026-tcs.json` — the generated test suite (e.g. tc0:
  `[[1,0,75],[2,0,76],[0,10,0],[0,7,76],[2,0,63],[0,9,0],[0,6,0]]` — 75-76 degree turns)
- `16-10-2026_team_tc_images_nsga2/run0/*.png` — rendered roads (gray) + car paths (blue dots)

## How it was run

```
cd tss/course-ambiegen
.venv/Scripts/python.exe runners/run_team_vehicle.py
```

`runners/run_team_vehicle.py` patches `config.vehicle_env` / `config.ga` /
`config.files` at runtime and registers `MountainVehicleProblem2Obj` as
`PROBLEMS["vehicle_nsga2"]` — **no repo file is modified**. Road images are
rendered by a pure-matplotlib renderer inside the driver because the
unmaintained `descartes` package crashes with shapely >= 2
(`IndexError` in `descartes/patch.py:63`, reproduced in this environment);
the driver renderer mirrors `VehicleSolution.build_image`
(`ambiegen/solutions/vehicle_solution.py:103-154`).
