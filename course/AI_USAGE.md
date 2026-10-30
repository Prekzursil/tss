# AI_USAGE.md — AI usage log for the AmbieGen course deliverable (Topic 4)

Required format per the course topic: **tool · purpose · prompt · result ·
edits · validation**. This file logs every use of AI tooling that contributed
to `deck.pptx`, `research.md`, `demo-run.md`, `demo-script.md`, `runners/`,
and `evidence/`.

**Honest scope statement.** This deliverable was produced *with* an AI coding
agent under team direction: the agent (ZCode CLI agent, powered by the GLM
model, driving a local Python 3.14 toolchain) did the source verification,
wrote and executed the runners, and generated the deck and documentation.
No other AI tools (ChatGPT, Copilot, Gemini, …) were used, and no AI tool was
used to *run experiments autonomously beyond the commands logged below* —
every optimization run is the AmbieGen-tool's own NSGA-II implementation,
executed with a fixed seed, with its raw output preserved under `evidence/`.
The team directed the work, chose the "Mountain Pass" scenario parameters,
reviewed every artifact, and is responsible for its content.

---

## Usage log

### 1. Source research and verification

| Field | Content |
|---|---|
| **Tool** | ZCode AI coding agent (GLM model) with web-fetch of the arXiv abstract + full HTML and a local shallow clone of the AmbieGen-tool repo (`git clone --depth 1`, 2026-10-16). |
| **Purpose** | Build a verified knowledge base for the talk: what AmbieGen is, its algorithms, fitness/novelty definitions, paper results, and repo rough edges — every claim tied to `paper §X` or `repo path:line`. |
| **Prompt** (paraphrased task given to the agent) | "Course topic: automatic search-based test case generation for autonomous systems with AmbieGen. Study the paper (arXiv 2301.01234) and the tool repo; verify claims against the actual code; produce a research knowledge base. The presentation must document AI usage (AI_USAGE.md: tool, purpose, prompt, result, edits, validation) and include a bibliography." |
| **Result** | `research.md` (8 sections, source index in §8). Notable verified findings: the README's `--algo` flag does not exist (real flag `--algorithm`, `optimize.py:58`); `requirements.txt` omits scipy/matplotlib/descartes; pymoo must be pinned to 0.6.0; no "smart home" case study exists in paper or repo (§1 warning). |
| **Edits** | Team reviewed the knowledge base; the §1 "smart home" warning and the §6 new-SUT recipe were kept explicitly because the course asks for a team case study. |
| **Validation** | Every code claim in `research.md` carries a `path:line` citation into the local clone (e.g. `vehicle_problem.py:64`, `optimize.py:58`); paper claims cite fetched arXiv HTML sections; the CLI claims were checked live via `python optimize.py --help` (§7). |

### 2. Environment setup and smoke runs

| Field | Content |
|---|---|
| **Tool** | ZCode agent driving the shell (Windows, Python 3.14.6, cmd/bash). |
| **Purpose** | Make the cloned tool actually run on this machine and learn its real failure modes. |
| **Prompt** | "Install and run AmbieGen-tool locally; record exactly what works and what breaks on this Python." |
| **Result** | Pinned `requirements.txt` fails on Python 3.14 (`Shapely 1.8.4` does not build); working set: `pymoo==0.6.0` + current shapely/pandas/numpy/scipy/matplotlib/descartes; pymoo ≥ 0.6.1 crashes the repo (`KeyError: 'algorithm'`); vehicle image rendering crashes under shapely ≥ 2 (`descartes/patch.py:63 IndexError`). All recorded in `research.md` §7 and `demo-run.md` §0. |
| **Edits** | None — raw observations. |
| **Validation** | The failing commands and their exact error text are quoted in `demo-run.md` §0; the working install line is the one the runbook uses. |

### 3. Case-study runner scripts and evidence capture

| Field | Content |
|---|---|
| **Tool** | ZCode agent writing and executing `runners/run_builtin_robot.py` and `runners/run_team_vehicle.py` (the team supplied the "Mountain Pass" parameter choices: `max_len` 30→12, `min_angle` 10→25, failure threshold 5→6). |
| **Purpose** | Run (a) the built-in robot case study and (b) the team "Mountain Pass" scenario, both NSGA-II, seed 42, bounded budget pop 20 × 15 gens, suite of 5; capture logs, stats, test cases and images as graded evidence. |
| **Prompt** | "Run both case studies without modifying any repo file; save outputs under evidence/ and write the scenario diff." |
| **Result** | Builtin run: 85.5 s wall clock, best A* path 132.1, novelty 0.437. Team run: 5.9 s, best lane deviation 4.649 (bar 6), cv_min 2.357→1.351, novelty 0.583. Artifacts: `evidence/builtin/`, `evidence/team/` (run logs, stats/conv JSON, test-case JSON, 5 PNGs each, `team_scenario_config.json`, `evidence/team/README.md`). |
| **Edits** | Team chose the scenario parameters and failure threshold; agent implemented them via runtime config patch + `MountainVehicleProblem2Obj` subclass (zero repo files modified) and a matplotlib road renderer replacing the crashing descartes path. |
| **Validation** | Both runs executed to completion on 2026-10-16 with `random_seed=42`; raw stdout preserved in `evidence/*/run_log.txt`; numbers on the slides were copied from those logs. A later accidental re-import (critic round 1, see §5) regenerated the date-prefixed working folders inside `AmbieGen-tool/` — verified **byte-identical** to the graded `evidence/` copies (deterministic seed), so graded artifacts are unaffected. |

### 4. Deck generation and QA

| Field | Content |
|---|---|
| **Tool** | ZCode agent generating `build_deck.py` (python-pptx 1.0.2; method follows the pptx skill: palette, sandwich structure, one motif, source line per slide) and `qa_deck.py` (overflow/placeholder/bounds checker). |
| **Purpose** | Produce the 20-slide, two-presenter deck `deck.pptx` plus the demo runbook `demo-run.md` and minute-by-minute `demo-script.md`. |
| **Prompt** | "Build the presentation: two presenters × 10 min, every key figure backed by paper/repo/evidence, live-demo pointers included." |
| **Result** | `deck.pptx` (native charts for the paper's 9-vs-2 and 14-vs-9 results and our convergence curves, embedded evidence images), `demo-run.md`, `demo-script.md`. |
| **Edits** | Team reviewed slide content against the rubric. Round-1 critic fixes applied (see §5): full 7-segment tc0 genome on slide 7, explicit scope note on slide 15, new References slide 19. |
| **Validation** | `python build_deck.py` regenerates the deck deterministically; `python qa_deck.py` reports no overflow/placeholder/bounds issues; the deck is re-opened with python-pptx after every rebuild (slide count and spot-checked text asserted). |

### 5. Round-1 critic fixes (2026-10-16, this pass)

| Field | Content |
|---|---|
| **Tool** | ZCode agent (GLM model). |
| **Purpose** | Repair the five findings from the round-1 presentation critic. |
| **Prompt** | "Fix the course deliverable: (1) AI_USAGE.md missing — create it; (2) team case study reuses the built-in SUT — make the scope explicit; (3) slide 7 shows a 5-element prefix of a 7-element genome — show it verbatim; (4) run_builtin_robot.py runs at import — add a `__main__` guard; (5) no references slide — add one. Re-verify the deck opens via python-pptx." |
| **Result** | This file; scope note added to slide 15 and `research.md` §6; slide 7 now shows tc0's full 7 segments; `runners/run_builtin_robot.py` guarded; References slide added (deck now 20 slides); `demo-script.md` slide references updated. |
| **Edits** | All edits listed above are AI-made and team-visible in this pass. |
| **Validation** | Receipts: import test `.venv/Scripts/python.exe -c "import run_builtin_robot"` completes in ~1.3 s without running the optimization; deck rebuilt and re-opened via python-pptx (20 slides; slide 7 genome text matches `evidence/team/16-10-2026_team_tcs_nsga2/16-10-2026-tcs.json` tc0 exactly); `qa_deck.py` clean; working folders byte-compared against `evidence/`. |

---

## What was NOT AI-generated

- The experimental *results* themselves: every number in the deck comes from
  NSGA-II runs of the unmodified AmbieGen-tool code (seed 42), preserved in
  `evidence/`. The AI wrote the driver scripts, not the search algorithm.
- The "Mountain Pass" scenario design (which parameters to tighten and why)
  was the team's decision, implemented by the agent as directed.

## Reproducing the validation

```bat
cd tss\course-ambiegen
python build_deck.py                     :: rebuild deck.pptx deterministically
python qa_deck.py                        :: overflow / placeholder / bounds check
python -c "from pptx import Presentation; p=Presentation('deck.pptx'); print(len(p.slides._sldIdLst))"
.venv\Scripts\python.exe runners\run_builtin_robot.py   :: Demo A (~86 s)
.venv\Scripts\python.exe runners\run_team_vehicle.py    :: Demo B (~6 s)
```
