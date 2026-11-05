# TSS Lab Presentation Package

Everything needed to understand, run, submit, and present the individual TSS lab
("Systematic Black-Box Testing of an E-Commerce Pricing Module"),
Andrei Mihai Visalon — FMI, Master IS, 2026-2027.

## Read in this order

| # | File | What it is |
|---|------|-----------|
| 1 | `TSS_Lab_Presentation.pptx` | The 13-slide deck you present (speaker notes on every slide, Step 1 → Step 7 → Results → AI usage & contribution → Takeaways) |
| 2 | `TSS_Lab_Documentation.docx` / `TSS_Lab_Documentation.pdf` | The full end-to-end documentation (Word + PDF ready to send/upload): functions specified & why, all 7 requirements + Phase 7, live-demo guide, expected questions + answers |
| 3 | `FUNCTIONS.md` | Quick-reference: every function, its exact signature, fault sites, worked examples, which suite tests it |
| 4 | `SPEC.md` | The black-box specification (the requirements baseline from which the EP, BVA and CEG tests derive; MC/DC takes its conditions from the code) |
| 5 | `pricing.py` | The module under test (stdlib-only port, 57 statements, 22 branches) |
| 6 | `tests/` | The five suites: `test_ep.py` (52), `test_bva.py` (129), `test_ceg.py` (17), `test_mcdc.py` (14) = 212 example-based tests + `test_properties.py` (8 Hypothesis properties) = **220 tests total** |
| 7 | `mutants/` | The three hand-built order-1 mutants (`mutant_equivalent.py`, `mutant_killed.py`, `mutant_surviving.py`) + `run_demo.py` |
| 8 | `docs/` | Derivation & analysis documents: `ep.md`, `bva.md`, `ceg.md`, `mcdc.md`, `cfg.drawio`, `cfg.svg`, `cfg-analysis.md`, `gen_cfg.py`, `coverage-comparison.md`, `mutants-manual.md`, `mutation-analysis.md` |
| 9 | `README.md`, `REPORT.md`, `AI_USAGE.md` | The delivered lab overview, technical report, and mandatory AI usage log |
| 10 | `run_lab.ps1`, `run_lab.sh` | One-command test & demo runners for PowerShell and Bash |

## Run everything locally (from this folder)

**Setup, once:** Python 3.10 or newer, then install the three test tools declared
in `pyproject.toml`:

```powershell
python -m pip install "pytest>=8" "pytest-cov>=5" "hypothesis>=6"
```

Without this step the runners stop with `No module named pytest`.

Using the helper scripts (PowerShell or Git Bash / WSL):

```powershell
# PowerShell:
.\run_lab.ps1 all          # Run full verification (220 tests + 100% coverage + 69 CFG checks + mutation demo)
.\run_lab.ps1 coverage     # Run Req 2 separate per-suite coverage comparison (EP, BVA, CEG, MC/DC, Combined)
.\run_lab.ps1 cfg          # Run Req 3 CFG + V(G)=19 + 19 basis-path verifier (69 checks)
.\run_lab.ps1 mutants      # Run Req 5-6 hand-built mutants demo (equivalent, killed, surviving)
.\run_lab.ps1 properties   # Run Phase 7 Hypothesis property-based tests (use .\run_lab.ps1 deep for 10,000 examples)
```

```bash
# Bash (Git Bash / WSL / Linux):
./run_lab.sh all
./run_lab.sh coverage
./run_lab.sh cfg
./run_lab.sh mutants
```

Or directly via `python`:

```powershell
python -m pytest --cov --cov-branch
python docs/gen_cfg.py
python mutants/run_demo.py
```

The repo of record (CI-enforced, all checks green):
**github.com/Prekzursil/tss** → `lab/`.
