# TSS — Software Systems Testing

Course project for **TSS (Testarea Sistemelor Software)**, FMI Master IS, 2026-2027.

## Structure

### `lab/` — Systematic Testing Lab (7 requirements)

Testing the e-commerce pricing module (fee/VAT/totals with configurable rounding):

- **Functional testing**: equivalence partitioning (52 tests), boundary value analysis (129), cause-effect graphing (17) — 198 test derivation + pytest implementation
- **Structural testing**: control-flow graph (51 nodes, 62 edges, V(G)=19), cyclomatic complexity, basis path set, code coverage comparison (coverage.py via pytest-cov)
- **MC/DC**: modified condition/decision coverage with truth-table justification
- **Property-based testing**: 8 Hypothesis invariants over the whole input space (quantization Q1–Q2, totals T1–T4, fee F1, VAT V1) — 200 examples each in CI, 10 000 each in the deep `SLOW=1` pass
- **Mutation testing**: hand-crafted mutants (equivalent, killed, surviving) + mutation scores via **mutmut** and **cosmic-ray** (176 + 226 mutants)
- **220 lab tests** (238 across the repo), 100% line + branch coverage on `lab/pricing.py`
- **Submission documents**: `lab/TSS_Lab_Documentation.pdf` (+ `.docx`) and `lab/TSS_Lab_Presentation.pptx`; plain-language guide to every term in `lab/README.md`; contribution declaration and AI-usage log in `lab/README.md` and `lab/AI_USAGE.md`
- **One-command runners**: `lab/run_lab.ps1` / `lab/run_lab.sh` (`all`, the per-suite targets, `coverage`, `cfg`, `mutants`, `deep`)

### `course/` — Topic 4: AmbieGen (Search-Based Test Generation for Autonomous Systems)

Presentation + live demo of AmbieGen framework:

- **20-slide deck** (two presenter parts)
- **Team case study "Mountain Pass"**: new LKAS vehicle scenario (max_len 30→12, min_angle 10→25, failure threshold 5→6) with NSGA-II optimization
- Built-in robot case study reproduction
- Upstream documentation errata filed (reward_basis data/docs mismatch)
- Research notes, demo script, evidence directory

## Tech Stack

Python (pytest, pytest-cov/coverage.py, hypothesis, mutmut, cosmic-ray), NSGA-II optimization, AmbieGen framework
