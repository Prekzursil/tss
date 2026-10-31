# QZP Onboarding — Finish Report (`Prekzursil/tss`)

Branch `main` @ `1a0a504` (merge commit of PR #1). All facts below were read
from this tree or via the GitHub API / `gh` CLI on 2026-10-31.

## 1. What was onboarded (PR #1, `chore/qzp-onboarding`)

Four commits, merged as `1a0a504` at 2026-10-31T19:47:39Z:

| Commit | What |
|---|---|
| `ff95412` | The onboarding itself: CI + quality + CodeQL workflows, dependabot, community files, root `pyproject.toml`, `qa_deck.py` fix, `gen_cfg.py` lint fix, test-suite lint pass |
| `1c95359` | QZP pin bump `48e1e5c` → `0c4b8c6` + `requirements.txt` manifest (gate failures fixed) |
| `a97ecc4` | basedpyright standard-mode clean |
| `58dfce3` | `Pillow>=13.0.0` floor in `requirements.txt` (OSV zero-tolerance) |

### Workflows (`.github/workflows/`)

- **`ci.yml` (`tss-ci`)** — native CI, no QZP dependency. Matrix
  `ubuntu-latest` + `windows-latest` × Python `3.10` + `3.12`
  (`fail-fast: false`). Steps: compile-check of every tracked `.py`
  (excludes `.venv/`, `AmbieGen-tool/`; one file at a time so a failure names
  itself), then `pytest --cov --cov-branch` with the 100% gate enforced by
  `pyproject.toml` (`fail_under = 100`). Coverage XML uploaded from the
  ubuntu/py3.12 leg. Actions pinned by SHA: `checkout@11d5960a` (v4),
  `setup-python@a26af69` (v5), `upload-artifact@ea165f8d` (v4).
- **`quality.yml` (`quality`)** — thin caller of
  `Prekzursil/quality-zero-platform/.github/workflows/reusable-quality.yml@0c4b8c63d3ca41fffdf70ecd36cc96f46eb5c6e1`
  with `deps-severity-floor: any` (zero tolerance: any finding of any
  severity fails). Runs on push/PR to `main` + `merge_group`. PR runs are
  cancelled on supersede; default-branch runs always finish.
- **`codeql.yml` (`CodeQL`)** — thin caller of
  `Prekzursil/quality-zero-platform/.github/workflows/reusable-codeql.yml@0c4b8c63d3ca41fffdf70ecd36cc96f46eb5c6e1`
  (same pin), passing `repo_slug`, `event_name`, `sha`,
  `platform_repository`/`platform_ref`. Triggers: push/PR to `main`/`master`,
  `merge_group`, weekly schedule (`23 3 * * 1`), manual.

### QZP pins

- Initially both reusable-workflow pins were
  `@48e1e5c86e053b39d73277a32936213ffbb75a89` (commit `ff95412`).
- CodeQL then failed with `KeyError: Repo Prekzursil/tss not found in
  inventory` — `reusable-codeql.yml` checks QZP out at its own pinned commit
  (`48e1e5c8`), whose inventory predates the `tss` enrollment (QZP PR #359,
  merged as `0c4b8c63`). Commit `1c95359` bumped **both** pins to the
  enrollment merge commit `0c4b8c63d3ca41fffdf70ecd36cc96f46eb5c6e1` — the
  documented adoption path. Gate changes happen in quality-zero-platform,
  never here; this repo adopts them by bumping the pin.

### Community files

- `LICENSE` (MIT), `SECURITY.md`, `CONTRIBUTING.md`
- `.github/CODEOWNERS` (`* @Prekzursil`), `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/feature_request.yml`
- Supporting config shipped alongside: `.github/dependabot.yml`
  (github-actions + pip ecosystems, weekly, grouped patch/minor,
  semver-major ignored, 10 open PRs each), `.gitleaks.toml` (default rules,
  deliberately empty allowlist), `codecov.yml`, root `pyproject.toml`,
  `requirements.txt`.

## 2. The gates and their config

| Gate | Workflow | Config highlights |
|---|---|---|
| Tests + coverage | `tss-ci` | 2 OS × 2 Python versions; compile-check all tracked `.py`; `--cov --cov-branch`; `[tool.coverage.report] fail_under = 100`, `branch = true`, `source = ["lab", "course"]` with an explicit `omit` list |
| Lint + format | `quality` (ruff) | `line-length = 100`, `target py310`, rules `E,F,W,I,UP,B`; per-file style relaxations with written rationale (`build_deck.py`, `gen_cfg.py`: `E501,UP031,E702,B007`; frozen `lab/pricing.py`: `I001` only); ruff-format excludes frozen/doc-coupled files (`pricing.py`, `gen_cfg.py`, `*.md`, `docs/**`) |
| Types | `quality` (basedpyright) | `typeCheckingMode = "standard"`, `pythonVersion = "3.10"`, `reportMissingImports = "warning"`; excludes `AmbieGen-tool`, `lab/mutants`, `course/runners`, `build_deck.py`. Bar is **0 errors AND 0 warnings** — which is why `requirements.txt` exists: the gate installs it before the type lane so `pptx`/`pytest` imports resolve (the flat `lab/`+`course/` layout cannot be built by `pip install .`) |
| SAST | `quality` (opengrep) + `CodeQL` | opengrep inside the zero-tolerance reusable gate; CodeQL via the pinned reusable caller |
| Secrets | `quality` (gitleaks) | default ruleset; allowlist kept empty by policy |
| Dependencies | `quality` (osv-scanner) | `deps-severity-floor: any` → every open advisory blocks. This forced the `Pillow>=13.0.0` floor (`58dfce3`): the unpinned transitive resolved at python-pptx's declared minimum 9.5.0, which carries 53 open advisories (5 Critical / 34 High; newest fixed only in 13.0.0). Verified with the gate's pinned binary (osv-scanner v2.3.8) |
| Coverage (Codecov) | `codecov.yml` | `range: "100...100"`, project + patch targets 100%, threshold 0%, `require_ci_to_pass: true`; same `ignore` list as coverage.py |

## 3. Coverage scope, stated honestly

The measured 100% line+branch scope is deliberately bounded and the boundary
is documented in two places that must stay in sync:

- **`CONTRIBUTING.md` → "Coverage scope, stated honestly"** — the canonical
  human-readable statement.
- **`pyproject.toml` → `[tool.coverage.run]`** — the enforced `omit` list
  with per-entry rationale.

Measured (enforced, not aspirational): `lab/pricing.py` (212 tests, the
systematic-testing analysis target) and `course/qa_deck.py` (18 tests on
synthetic decks). Deliberately outside: `course/build_deck.py` (output QA'd
via `qa_deck.py` on the committed `deck.pptx`), `course/runners/*.py`
(AmbieGen experiment drivers needing the un-vendored upstream clone),
`lab/mutants/*.py` (mutation scores are the delivered evidence), and
`lab/docs/gen_cfg.py` (self-verifying committed CFG artifacts).

## 4. tss-only code fixes that came with onboarding

Scope note: this report covers **`tss` only**. The 3 latent crash bugs fixed
in the *tsis* repo are a separate workstream and are intentionally **not**
listed here. What landed in this repo:

1. **`course/qa_deck.py` path bug** (`ff95412`) — the module executed
   `Presentation(PATH)` at import time with a stale hardcoded absolute path
   pointing at the pre-rename `tss/course-ambiegen/` directory, so importing
   it outside that exact location crashed. Rewritten argv-driven and
   import-safe: functions instead of module-level execution, deck path
   defaults to `deck.pptx` next to the script, exit code 0/1 (CI-friendly).
   Accompanied by `course/tests/test_qa_deck.py` — 18 new tests at 100%
   line+branch on the file, including a run over the committed deck.
2. **`lab/docs/gen_cfg.py` lint fixes** (`ff95412`) — removed the dead
   assignment `y_top, y_bot` in `edge_geometry` and made the zip pairing
   explicit with `zip(steps, steps[1:], strict=False)` in `verify_basis`.
   Self-verification still passes (`ALL CHECKS PASSED`); the file is frozen
   (doc-coupled output) so nothing else moved.
3. **basedpyright standard-mode cleanups** (`a97ecc4`) — kwargs dicts in the
   lab test helpers annotated `dict[str, Any]` (dynamic-kwargs harness;
   `**`-unpacking into typed params unions spuriously); targeted
   `pyright:ignore[reportArgumentType]` on the 8 `test_ep.py` negative-test
   lines that intentionally pass invalid types; dropped class-style
   annotations on python-pptx's `Presentation` factory in `test_qa_deck.py`;
   4 ElementTree-Optional `pyright:ignore`s in frozen `gen_cfg.py`; I001
   import-order fixes in the three test files. Result: basedpyright standard
   **0 errors / 0 warnings** at the gate's pinned tool version (1.39.8).

## 5. Current status

Verified 2026-10-31 via `gh api`/`gh run list` and a local suite run.

| Item | State | Evidence |
|---|---|---|
| `main` @ `1a0a504` — `tss-ci` | ✅ green | check-runs on the merge commit: `verify (ubuntu-latest, py3.10/3.12)` + `verify (windows-latest, py3.10/3.12)` all `success` |
| `main` @ `1a0a504` — `quality` | ✅ green | `quality / quality -> success` |
| `main` @ `1a0a504` — `CodeQL` | ✅ green | `codeql / CodeQL -> success` (analyze + resolve profile) |
| PR #1 | ✅ MERGED | merged 2026-10-31T19:47:39Z, merge commit `1a0a504` |
| Ruleset | ✅ active | `quality-zero-platform / tss` (id 26286012), branch ruleset on `refs/heads/main`: PRs required (0 approvals, extra approval required for unattributed changes), 6 required status checks (4× `verify` matrix + `quality / quality` + `codeql / CodeQL`, strict policy), no force-push, no deletion, code-scanning rule (CodeQL, all alert thresholds) |
| CodeQL alerts | ⚠️ 3 open, all severity **note** | #1 `py/empty-except` `course/build_deck.py:142`, #2 `py/empty-except` `course/build_deck.py:296`, #3 `py/unused-import` `course/runners/run_team_vehicle.py:27` |
| Open PRs | 5 | #5 removes the unused `import copy` (resolves alert #3; #1/#2 deliberately reported-not-auto-fixed as semantic decisions); #2/#3/#4 dependabot manifest updates (pytest ≥9.2.0, pytest-cov ≥7.1.0, python-pptx ≥1.0.2) |
| Local suite (this checkout, `.venv` py3.14.6) | ✅ | `pytest --cov --cov-branch` → **230 passed, 100.00% line+branch** on `lab/pricing.py` + `course/qa_deck.py` |

Note on the alerts: the three open CodeQL findings are note-level and the
code-scanning ruleset rule thresholds are `all`, so they will block future
PRs to `main` until triaged via PR #5 (#3) and an owner decision on the two
`empty-except` blocks in `build_deck.py` (#1, #2 — that file is outside the
measured coverage scope and its per-file lint relaxation does not extend to
CodeQL).
