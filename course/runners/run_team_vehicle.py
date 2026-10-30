"""
TEAM CASE STUDY: "Mountain Pass" — a new road/environment scenario for the
built-in vehicle (LKAS) system under test.

What is new vs. the shipped vehicle scenario (config.py:5-11):
  * max_len     30 -> 12 : straights are capped at 12 units -> no long stable
                           stretches for the lane-keeping controller to settle
  * min_angle   10 -> 25 : every turning segment rotates >= 25 degrees ->
                           sustained, hairpin-like curvature
  * failure threshold 5 -> 6 : a test case is "fault revealing" only when the
                           car's max deviation from the lane centreline
                           exceeds 6 (team-defined criterion; shipped code
                           uses 5 at ambiegen/problems/vehicle_problem.py:64)

Repo files are NOT modified:
  * the scenario is configured through the repo's native format, the
    `vehicle_env` dict in config.py, patched at runtime;
  * the stricter threshold is registered by subclassing VehicleProblem2Obj
    and rebinding PROBLEMS["vehicle_nsga2"] (optimize.py looks it up at call
    time, optimize.py:113);
  * road images are rendered with a pure-matplotlib renderer because the
    unmaintained `descartes` package crashes with shapely >= 2
    (IndexError in descartes/patch.py:63, verified in this environment);
    the renderer mirrors VehicleSolution.build_image
    (ambiegen/solutions/vehicle_solution.py:103-154).
"""
import copy
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AmbieGen-tool"))
sys.path.insert(0, REPO)
os.chdir(REPO)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
from shapely.geometry import LineString

import config as cf

# ------------------------------------------------------------------
# 1) TEAM SCENARIO: "Mountain Pass" road environment
# ------------------------------------------------------------------
TEAM_VEHICLE_ENV = {
    "map_size": 200,   # unchanged
    "min_len": 5,      # unchanged
    "max_len": 12,     # WAS 30 - short straights only
    "min_angle": 25,   # WAS 10 - every segment turns >= 25 deg
    "max_angle": 80,   # unchanged
}
TEAM_FAILURE_THRESHOLD = 6  # WAS 5 - stricter fault-revealing criterion

cf.vehicle_env.update(TEAM_VEHICLE_ENV)

# bounded budget, identical to the builtin robot run for comparability
cf.ga.update({"pop_size": 20, "n_gen": 15, "mut_rate": 0.4, "cross_rate": 0.9,
              "test_suite_size": 5})

# distinct output folder prefixes so team results never clobber builtin ones
cf.files.update({"stats_path": "team_stats", "tcs_path": "team_tcs",
                 "images_path": "team_tc_images"})

# ------------------------------------------------------------------
# 2) Team problem class: same 2 objectives, stricter failure constraint
# ------------------------------------------------------------------
from ambiegen.problems import PROBLEMS
from ambiegen.problems.vehicle_problem import VehicleProblem2Obj


class MountainVehicleProblem2Obj(VehicleProblem2Obj):
    """VehicleProblem2Obj with the team's stricter failure threshold."""

    def _evaluate(self, x, out, *args, **kwargs):
        super()._evaluate(x, out, *args, **kwargs)
        # shipped: out["G"] = 5 - fitness*(-1)  (vehicle_problem.py:64)
        out["G"] = TEAM_FAILURE_THRESHOLD - out["F"][0] * (-1)


PROBLEMS["vehicle_nsga2"] = MountainVehicleProblem2Obj

# ------------------------------------------------------------------
# 3) descartes-free road renderer (same visual semantics as the original)
# ------------------------------------------------------------------
from ambiegen.utils.car_road import Map
from ambiegen.utils.vehicle_evaluate import evaluate_scenario, interpolate_road


def render_road_image(states, save_path="test.png"):
    map_size = cf.vehicle_env["map_size"]
    test_map = Map(map_size)
    road_points, new_states = test_map.get_points_from_states(states)
    intp_points = interpolate_road(road_points)
    fitness, car_path = evaluate_scenario(intp_points)

    fig, ax = plt.subplots(figsize=(8, 8))
    road_x = [p[0] for p in intp_points]
    road_y = [p[1] for p in intp_points]

    if len(car_path):
        ax.plot(car_path[0], car_path[1], "bo", label="Car path")
    ax.plot(road_x, road_y, "yo--", label="Road")

    road_poly = LineString([(t[0], t[1]) for t in intp_points]).buffer(
        8.0, cap_style=2, join_style=2)
    if not road_poly.is_empty:
        ax.add_patch(MplPolygon(np.asarray(road_poly.exterior.coords), closed=True,
                                fc="gray", ec="dimgray"))

    ax.set_title("Test case fitness " + str(fitness), fontsize=17)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.set_ylim(0, map_size)
    ax.set_xlim(0, map_size)
    ax.legend(fontsize=16)
    plt.ioff()
    fig.savefig(save_path)
    plt.close(fig)


def team_save_tcs_images(test_suite, problem, run, algo):
    """Same contract as ambiegen.utils.save_tcs_images, using our renderer."""
    from datetime import datetime
    dt_string = datetime.now().strftime("%d-%m-%Y")
    images_path = dt_string + "_" + cf.files["images_path"] + "_" + algo
    os.makedirs(os.path.join(images_path, "run" + str(run)), exist_ok=True)
    for i in range(len(test_suite)):
        path = os.path.join(images_path, "run" + str(run), str(i) + ".png")
        render_road_image(test_suite[str(i)], path)
    print(f"[team] images saved in {images_path}")


import optimize
optimize.save_tcs_images = team_save_tcs_images  # rebind name used by main()

# ------------------------------------------------------------------
# 4) run
# ------------------------------------------------------------------
if __name__ == "__main__":
    evidence_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "evidence", "team"))
    with open(os.path.join(evidence_dir, "team_scenario_config.json"), "w",
              encoding="utf-8") as f:
        json.dump({
            "scenario_name": "Mountain Pass (team case study)",
            "system_under_test": "vehicle LKAS simplified model",
            "vehicle_env": TEAM_VEHICLE_ENV,
            "vehicle_env_shipped_defaults": {
                "map_size": 200, "min_len": 5, "max_len": 30,
                "min_angle": 10, "max_angle": 80},
            "failure_threshold": TEAM_FAILURE_THRESHOLD,
            "failure_threshold_shipped_default": 5,
            "ga": cf.ga,
        }, f, indent=4)

    t0 = time.time()
    optimize.main(problem="vehicle", algo="nsga2", runs_number=1,
                  save_results=True, random_seed=42, debug=False)
    print(f"\n[run_team_vehicle] total wall time: {time.time() - t0:.1f}s")
