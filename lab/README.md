# TSS Lab — Black-box test design for the `pricing` module

## In plain words: what this lab does and why each part is needed

This lab checks one real piece of shop software: the code that works out a
customer's bill (subtotal, discount, delivery, an optional extra fee, and VAT).
It asks one question: **how do we know this code calculates correctly, and how
good are the checks we wrote for it?** Each assignment point answers part of
that question.

| Point | What it is, plainly | Why it is needed |
|---|---|---|
| Base | The billing code plus a written description of what it must do (`SPEC.md`) | You cannot test "correct" until you have written down what correct means. The specification is that yardstick; the EP, BVA and CEG tests are derived from it, not from the code (MC/DC, being structural, also reads the code's decisions). |
| 1a | **Equivalence partitioning** — group inputs that should behave the same way and test one from each group | There are endless possible bills, so you cannot try them all. Grouping lets a handful of tests stand in for whole families of inputs. |
| 1b | **Boundary value analysis** — test right at the edge of each group: zero, the limit, one step past it | Mistakes gather at edges: a `<` written instead of `<=`, a rounding cent off. The edges are where the bugs hide. |
| 1c | **Cause–effect graphing** — list the switches (fee on/off, VAT on/off, …) and the result each combination must give | Some faults appear only when two settings combine. This guarantees every combination that matters is tried. |
| 2 | **Coverage, per technique** — measure how much of the code each test set runs, each set on its own | A line that no test runs is a line no test can check. Running each set separately shows what each technique reaches and what it misses; BVA and CEG on their own miss a few lines *by design* (see `docs/coverage-comparison.md`), and all sets together reach 100%. |
| 3 | **Control-flow graph + cyclomatic complexity** — draw the code as a map of every decision and path, then count the independent paths | The count (19 here) is the size of a basis set: 19 independent routes that together drive every road through the logic. It is an upper bound on the tests needed to take every branch, not the minimum, and the map shows which routes those are. Closing each route with a return edge from its function's exit to its entry turns it into one of the 19 independent *circuits* the assignment asks for. |
| 4 | **MC/DC** — show that each individual condition can change the outcome on its own | Covering a decision is not enough: a condition that never really matters could be wrong without anyone noticing. MC/DC proves each one counts. It is required for the most safety-critical (Level A) flight software under DO-178C. |
| 5 | **Equivalent mutant** — a deliberate one-symbol change to the code that in fact changes nothing | It shows why a perfect mutation score is impossible: some changes have no visible effect, so no test could ever catch them. |
| 6 | **Killed vs. surviving mutant** — plant a small bug; one is caught by a test, one slips past it | It proves the tests are strong enough to catch a real fault, and shows exactly where a weaker test would let one through. |
| 7 | **Two mutation tools + mutation scores** — let tools plant hundreds of small bugs automatically and count how many the tests catch | This is the strongest automatic measure of test quality. Two tools are compared because they plant different kinds of bugs, so their scores differ for reasons you can explain. |
| Bonus | **Property-based testing** — state rules that must hold for any input (for example, the VAT is never negative) and try thousands of random inputs | It finds cases nobody thought to write by hand. |

**The idea behind the whole lab:** 100% coverage proves only that every line
*ran* during the tests. It does not prove the answers were *right*. A test can
run a line and check nothing. That is why the lab goes past coverage to
mutation testing, which asks the harder question: would these tests actually
notice if the code were wrong?

## Scope declaration

Per the assignment note, the **analysis scope is declared as the whole
`pricing` module** — the four public functions `quantize_money`,
`compute_fee`, `compute_vat`, `compute_totals` plus the `PricingBreakdown`
record (~4 functions). The module is a pure-stdlib
(`decimal` + `dataclasses`) port of the author's own repository code
(`momentstudio/backend/app/services/pricing.py`, fetched via GitHub API on
2026-10-16); behavior is identical, so results transfer to the original.

**Provenance, stated plainly.** The assignment asks for a program *and* its
requirements. Here the program pre-dates the lab (it is the author's own
production code), so [`SPEC.md`](SPEC.md) was derived by observing that
module's behavior rather than written before it. The assignment note permits
declaring a bounded scope; it does not by itself authorize spec-after-code
reuse — we rely instead on the transparent provenance above, on the fact that
the specification is written purely in black-box terms (no implementation
detail) and that the EP, BVA and CEG suites below are derived from the SPEC, not from the
code (MC/DC, being structural, takes its conditions from the code). AI tooling usage across all deliverables is logged in
[`AI_USAGE.md`](AI_USAGE.md).

- Requirements baseline: [`SPEC.md`](SPEC.md) — black-box specification
  (inputs, domains, rounding, fee/VAT/totals composition, error behavior).
  The EP, BVA and CEG suites are derived from it, not from the implementation; MC/DC, a structural criterion, takes its conditions from the code (docs/mcdc.md).

## Layout

```
lab/
├── pricing.py                    # module under test (ported, behavior-identical)
├── SPEC.md                       # black-box requirements specification (derivation source)
├── README.md                     # this file
├── REPORT.md                     # assembled technical report (tasks 1–7 + receipts)
├── AI_USAGE.md                   # AI usage log: tool/purpose/prompt/result/edits/validation
├── FUNCTIONS.md                  # quick-reference of all 4 functions + fault sites
├── PACKAGE.md                    # presentation package reading order & commands
├── TSS_Lab_Presentation.pptx     # 13-slide presentation deck with speaker notes
├── TSS_Lab_Documentation.docx    # full end-to-end documentation & Q&A guide (Word)
├── TSS_Lab_Documentation.pdf     # full end-to-end documentation & Q&A guide (PDF)
├── run_lab.ps1                   # PowerShell test & demo runner script
├── run_lab.sh                    # POSIX Bash test & demo runner script (LF)
├── pyproject.toml                # pytest + 100% branch coverage gate configuration
├── tests/
│   ├── conftest.py               # puts lab root on sys.path + registers Hypothesis profiles
│   ├── test_ep.py                # equivalence partitioning suite      (52 tests)
│   ├── test_bva.py               # boundary value analysis suite       (129 tests)
│   ├── test_ceg.py               # cause–effect graph / decision table  (17 tests)
│   ├── test_mcdc.py              # modified condition/decision coverage (14 tests)
│   └── test_properties.py        # Hypothesis property-based suite      (8 properties)
├── docs/
│   ├── ep.md                     # EP derivation (partition tables + traceability)
│   ├── bva.md                    # BVA derivation (boundary tables B1–B20)
│   ├── ceg.md                    # CEG graph + restricted-entry decision table
│   ├── mcdc.md                   # MC/DC derivation (condition pairs, truth tables)
│   ├── coverage-comparison.md    # per-suite vs combined coverage (point 2)
│   ├── cfg.drawio / cfg.svg      # control-flow graph (real draw.io XML + rendered SVG)
│   ├── cfg-analysis.md           # CFG construction, V(G), 19-path basis, infeasible-path analysis
│   ├── gen_cfg.py                # CFG generator + verifier (69 machine checks)
│   ├── mutants-manual.md         # the three hand mutants, equivalence proof, demo transcript
│   └── mutation-analysis.md      # mutmut + cosmic-ray × 4 suites: scores, survivors (point 7)
└── mutants/
    ├── mutant_equivalent.py      # order-1 mutant: final clamp `<` → `<=` (proven EQUIVALENT)
    ├── mutant_killed.py          # order-1 mutant: `fee_type == "percent"` → `!=` (KILLED)
    ├── mutant_surviving.py       # order-1 mutant: `fee_value <= 0` → `<= 4` (SURVIVES chosen test)
    └── run_demo.py               # sandboxed demo: chosen test + full suite per mutant, verdict checks
```

## Running

### Setup (once)

You need **Python 3.10 or newer**. Install the three test tools the lab uses —
these are exactly the versions declared in `pyproject.toml` under
`[project.optional-dependencies] test`:

```powershell
python -m pip install "pytest>=8" "pytest-cov>=5" "hypothesis>=6"
```

Without them the runners stop with `No module named pytest`. A virtual
environment is optional; if you create one, keep it outside this folder so the
submitted package stays clean.

### Run

Using the runner scripts (PowerShell or Git Bash / WSL):

```powershell
.\run_lab.ps1 all        # PowerShell: run all tests, coverage comparison, CFG verifier, mutation demo
./run_lab.sh all         # Bash: run all tests, coverage comparison, CFG verifier, mutation demo
```

Or directly with `python`:

Run everything with the 100% branch coverage gate:

```powershell
python -m pytest --cov=pricing --cov-branch --cov-fail-under=100
```

Run one suite with branch coverage on the module:

```powershell
python -m pytest tests/test_ep.py -q --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
```

(same form for `test_bva.py`, `test_ceg.py`, `test_mcdc.py`, `test_properties.py`). Coverage is
configured in `pyproject.toml`: `source = ["pricing"]`, `branch = true`, `fail_under = 100`. The `--cov-fail-under=0` above switches that gate off for a single-suite run: BVA, CEG and the property suite stay under 100% on their own, by design, and without the flag pytest prints `FAIL Required test coverage of 100.0% not reached` and exits 1 although every test passed.
Current stage: **complete** — 212 example-based tests + 8 Hypothesis property tests = **220 tests** collected, all green; combined line and branch coverage **100.00%** (57 statements, 22 branches, 0 missed).

## Assignment points 1–7 → artifacts

| Point | Deliverable | Artifacts |
|---|---|---|
| Base | Program + requirements | `pricing.py` (port of the author's module) + [`SPEC.md`](SPEC.md) |
| 1 | Black-box test generation & implementation (EP / BVA / CEG) | `tests/test_ep.py` + [`docs/ep.md`](docs/ep.md) (52) · `tests/test_bva.py` + [`docs/bva.md`](docs/bva.md) (129) · `tests/test_ceg.py` + [`docs/ceg.md`](docs/ceg.md) (17) |
| 2 | Per-suite coverage measurement & comparison | [`docs/coverage-comparison.md`](docs/coverage-comparison.md) |
| 3 | Control-flow graph, V(G), linearly independent basis paths | [`docs/cfg.drawio`](docs/cfg.drawio) + [`docs/cfg.svg`](docs/cfg.svg) + [`docs/cfg-analysis.md`](docs/cfg-analysis.md) + verifier [`docs/gen_cfg.py`](docs/gen_cfg.py) |
| 4 | Modified condition/decision coverage (MC/DC) | `tests/test_mcdc.py` + [`docs/mcdc.md`](docs/mcdc.md) (14) |
| 5–6 | Hand-built order-1 mutants: equivalent / killed / surviving + demo | [`mutants/`](mutants) (3 order-1 mutants + `run_demo.py`) + [`docs/mutants-manual.md`](docs/mutants-manual.md) |
| 7 | Two mutation-testing tools, mutation scores & operator analysis | [`docs/mutation-analysis.md`](docs/mutation-analysis.md) (mutmut 3.8.0 + cosmic-ray 8.7.0, each × 4 suites) |
| Bonus | Property-based testing with Hypothesis (Phase 7) | `tests/test_properties.py` (8 invariants, 200 examples/test by default, 10,000 with `SLOW=1`) |

## Contribution declaration (assignment points 1–7)

**Individual submission.** This lab was produced and is presented by a single
author, who directed, reviewed and takes responsibility for all seven points.

| Member | Points contributed to | Own percentage |
|---|---|---|
| Andrei Mihai Visalon | points 1–7 (all) | 100 % |

AI assistance for every deliverable is itemized in
[`AI_USAGE.md`](AI_USAGE.md); the declaration above concerns the author's own
direction, review and responsibility, stated in person at the presentation.
