## What & why

<!-- One-paragraph summary: what changes and the reason. -->

## Verification

<!-- How you proved it. Every claim needs a command + result. -->

- [ ] `python -m pytest --cov --cov-branch` — 100% line+branch, all green
- [ ] `ruff check .` and `ruff format --check .` — clean
- [ ] `quality` workflow green on this PR
- [ ] `CodeQL` workflow green on this PR

## Scope discipline

- [ ] No changes to measured results, evidence files, or `lab/pricing.py`
      (frozen analysis target) unless the PR explicitly re-baselines them
- [ ] Docs updated alongside any behavior change
