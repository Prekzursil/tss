# Contributing to `tss`

Thank you for improving this repository. It is a graded course deliverable
(FMI Master IS, TSS 2026–2027), so a few extra discipline rules apply on top
of normal open-source hygiene.

## The gates (all must be green)

Every push to `main` and every PR runs, via
[quality-zero-platform](https://github.com/Prekzursil/quality-zero-platform)
and native CI:

| Gate | What it enforces | Where |
|---|---|---|
| `tss-ci` | tests + **100% line AND branch coverage** on the measured scope, on ubuntu + windows, py3.10 + 3.12 | `.github/workflows/ci.yml` |
| `quality` | ruff lint+format, basedpyright (standard), coverage re-asserted, opengrep SAST, gitleaks, osv-scanner — **zero tolerance** (`deps-severity-floor: any`) | `.github/workflows/quality.yml` |
| `CodeQL` | code scanning, on push/PR/weekly | `.github/workflows/codeql.yml` |

Run locally before pushing:

```bash
python -m pip install "python-pptx>=1.0" "pytest>=8" "pytest-cov>=5" ruff
python -m pytest --cov --cov-branch   # must end at 100.00% and 0 failures
python -m ruff check .
python -m ruff format --check .
```

## Coverage scope, stated honestly

Measured at **100% line+branch** (enforced, not aspirational):

- `lab/pricing.py` — the systematic-testing analysis target (212 tests)
- `course/qa_deck.py` — the deck QA gate (18 tests on synthetic decks)

Deliberately **outside** the measured scope — one-shot experiment/artifact
generators whose *outputs* are the committed, QA'd deliverables
(see `pyproject.toml → [tool.coverage.run] omit`, with rationale):

- `course/build_deck.py` — generates the committed `deck.pptx`; verified by
  running `qa_deck.py` on the produced artifact
- `course/runners/*.py` — AmbieGen experiment drivers; require the upstream
  `AmbieGen-tool` clone which is intentionally not vendored
- `lab/mutants/*.py` — mutation-testing demo drivers; the mutation scores
  themselves are the delivered evidence
- `lab/docs/gen_cfg.py` — regenerates + self-verifies the committed CFG
  (`cfg.drawio`, `cfg.svg`; run it: `python lab/docs/gen_cfg.py` → must print
  `ALL CHECKS PASSED`)

## Frozen files

`lab/pricing.py` is the **frozen analysis target**: `SPEC.md`,
`lab/docs/cfg-analysis.md` and the mutant maps reference its exact line
structure. Do not reformat or reorder it; its ruff-format/import-sort is
pinned off in `pyproject.toml` for exactly that reason. Behavior-changing
edits require re-baselining every lab document in the same PR.

Never edit measured results or evidence files (`course/evidence/**`, results
tables in the docs) without re-running the experiment that produced them.

## Commits & PRs

- Branch from `main`; open a PR; both `quality` and `CodeQL` must be green.
- Conventional-ish subjects (`lab: …`, `course: …`, `ci: …`, `docs: …`).
- Fill the PR template — every claim needs a command + its output.

## Reporting bugs

See `SECURITY.md` for vulnerabilities, `.github/ISSUE_TEMPLATE/` for bugs.

## AI-tooling disclosure

This deliverable was produced with AI assistance; per-deliverable usage is
documented in `lab/AI_USAGE.md` and `course/AI_USAGE.md`. Contributions are
accepted regardless of tooling as long as the gates above pass and the
authorship is disclosed in the PR description.
