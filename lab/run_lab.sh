#!/usr/bin/env bash
# ==============================================================================
# TSS Lab Test & Presentation Runner (POSIX Bash / Git Bash / WSL)
# Systematic Black-Box & Structural Testing of an E-Commerce Pricing Module
# Author: Andrei Mihai Visalon — FMI, Master IS, 2026-2027
#
# Usage:
#   ./run_lab.sh [all|ep|bva|ceg|mcdc|properties|deep|coverage|cfg|mutants|clean]
# ==============================================================================
set -euo pipefail

LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_ROOT"

PYTHON_BIN="python"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
fi

TARGET="${1:-all}"

banner() {
    echo ""
    echo "=============================================================================="
    echo "  $1"
    echo "=============================================================================="
}

clean_caches() {
    rm -rf .coverage coverage.json .pytest_cache .hypothesis __pycache__ tests/__pycache__ mutants/__pycache__ docs/__pycache__
}

trap clean_caches EXIT

run_coverage_comparison() {
    banner "Requirement 2: Separate Per-Suite Code Coverage Comparison"
    "$PYTHON_BIN" -c '
import json, subprocess, sys
from pathlib import Path

suites = [
    ("EP (Req 1a)",       ["tests/test_ep.py"]),
    ("BVA (Req 1b)",      ["tests/test_bva.py"]),
    ("CEG (Req 1c)",      ["tests/test_ceg.py"]),
    ("MC/DC (Req 4)",     ["tests/test_mcdc.py"]),
    ("Combined (1-4)",    ["tests/test_ep.py", "tests/test_bva.py", "tests/test_ceg.py", "tests/test_mcdc.py"]),
    ("All (+Hypothesis)", ["tests"]),
]

print(f"{chr(39)+"Suite"+chr(39) if False else "Suite":<19} | {"Tests":>5} | {"Line Coverage":<18} | {"Branch Coverage":<18} | {"Missing Lines"}")
print("-" * 82)

cov_json = Path("coverage.json")
for label, paths in suites:
    if cov_json.exists():
        cov_json.unlink()
    cmd = [
        sys.executable, "-m", "pytest", *paths, "-q",
        "--cov=pricing", "--cov-branch",
        "--cov-report=json:coverage.json",
        "--override-ini=addopts=-p no:cacheprovider",
        "--cov-fail-under=0"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr)
        sys.exit(proc.returncode)
    data = json.loads(cov_json.read_text(encoding="utf-8"))
    f_info = next(v for k, v in data["files"].items() if k.endswith("pricing.py"))
    s = f_info["summary"]
    line_pct = (s["covered_lines"] / s["num_statements"]) * 100.0
    br_pct = (s["covered_branches"] / s["num_branches"]) * 100.0
    missing = ", ".join(str(x) for x in f_info["missing_lines"]) or "-"
    summary_line = [ln for ln in proc.stdout.splitlines() if "passed" in ln][-1]
    n_tests = summary_line.split()[0]
    c_l, n_s = s["covered_lines"], s["num_statements"]
    c_b, n_b = s["covered_branches"], s["num_branches"]
    print(f"{label:<19} | {n_tests:>5} | {line_pct:6.2f}% ({c_l}/{n_s})   | {br_pct:6.2f}% ({c_b}/{n_b})   | {missing}")

if cov_json.exists():
    cov_json.unlink()
'
}

# Single-suite targets (ep/bva/ceg/mcdc/properties) are measurements for Requirement 2,
# not the gate: BVA, CEG and the property suite are expected to stay under 100% on their
# own. --cov-fail-under=0 switches off pyproject.toml's fail_under = 100 for those runs
# only; the 100% gate still runs on the full suite in the 'all' target.
case "$TARGET" in
    ep)
        banner "Requirement 1a: Equivalence Partitioning (52 tests)"
        "$PYTHON_BIN" -m pytest tests/test_ep.py -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
        ;;
    bva)
        banner "Requirement 1b: Boundary Value Analysis (129 tests)"
        "$PYTHON_BIN" -m pytest tests/test_bva.py -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
        ;;
    ceg)
        banner "Requirement 1c: Cause-Effect Graphing (17 tests)"
        "$PYTHON_BIN" -m pytest tests/test_ceg.py -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
        ;;
    mcdc)
        banner "Requirement 4: Modified Condition/Decision Coverage (14 tests)"
        "$PYTHON_BIN" -m pytest tests/test_mcdc.py -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
        ;;
    properties)
        banner "Phase 7: Hypothesis Property-Based Testing (8 properties x 200 examples)"
        "$PYTHON_BIN" -m pytest tests/test_properties.py -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
        ;;
    deep)
        banner "Phase 7 Deep Run: Hypothesis Property-Based Testing (SLOW=1, 10,000 examples/property)"
        SLOW=1 "$PYTHON_BIN" -m pytest tests/test_properties.py -v --hypothesis-show-statistics
        ;;
    coverage)
        run_coverage_comparison
        ;;
    cfg)
        banner "Requirement 3: Control-Flow Graph, V(G)=19 & 19 Basis-Path Verifier"
        "$PYTHON_BIN" docs/gen_cfg.py
        ;;
    mutants)
        banner "Requirements 5 & 6: Hand-Built Order-1 Mutants Demo (Equivalent, Killed, Surviving)"
        "$PYTHON_BIN" mutants/run_demo.py
        ;;
    clean)
        clean_caches
        echo "[OK] Cleaned temporary test/coverage caches."
        ;;
    all)
        banner "STEP 1/4: Full Test Suite (220 tests) + 100% Line & Branch Coverage Gate"
        "$PYTHON_BIN" -m pytest --cov=pricing --cov-branch --cov-fail-under=100
        run_coverage_comparison
        banner "STEP 3/4: Requirement 3 - Control-Flow Graph, V(G)=19 & 19 Basis-Path Verifier"
        "$PYTHON_BIN" docs/gen_cfg.py
        banner "STEP 4/4: Requirements 5 & 6 - Hand-Built Mutants Live Demo"
        "$PYTHON_BIN" mutants/run_demo.py
        banner "ALL TSS LAB CHECKS PASSED (220/220 TESTS, 100% LINE+BRANCH, 69 CFG CHECKS, 3/3 MUTANT CLAIMS)"
        ;;
    *)
        echo "Usage: $0 [all|ep|bva|ceg|mcdc|properties|deep|coverage|cfg|mutants|clean]"
        exit 1
        ;;
esac
