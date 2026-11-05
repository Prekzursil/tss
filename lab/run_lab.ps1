<#
.SYNOPSIS
    TSS Lab Test & Presentation Runner (PowerShell 7 / Windows PowerShell)
    Systematic Black-Box & Structural Testing of an E-Commerce Pricing Module
    Author: Andrei Mihai Visalon - FMI, Master IS, 2026-2027

.DESCRIPTION
    Executes individual test suites, separate per-suite coverage comparison (Req 2),
    CFG & Cyclomatic Complexity V(G)=19 verification (Req 3), MC/DC (Req 4),
    hand-built mutants live demo (Req 5-6), Hypothesis property tests (Phase 7),
    or the complete end-to-end lab verification (`all`).

.PARAMETER Target
    One of: all, ep, bva, ceg, mcdc, properties, deep, coverage, cfg, mutants, clean
    Defaults to 'all'.

.EXAMPLE
    .\run_lab.ps1
    .\run_lab.ps1 coverage
    .\run_lab.ps1 mutants
    .\run_lab.ps1 cfg
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "ep", "bva", "ceg", "mcdc", "properties", "deep", "coverage", "cfg", "mutants", "clean")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$LabRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $LabRoot

function Write-Banner([string]$Title) {
    Write-Host ""
    Write-Host ("=" * 78) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 78) -ForegroundColor Cyan
}

function Invoke-Clean {
    $paths = @(".coverage", "coverage.json", ".pytest_cache", ".hypothesis", "__pycache__", "tests\__pycache__", "mutants\__pycache__", "docs\__pycache__")
    foreach ($p in $paths) {
        if (Test-Path $p) {
            Remove-Item -Recurse -Force $p -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-SingleSuite([string]$Name, [string]$File) {
    Write-Banner "Running $Name ($File)"
    # One suite on its own is a measurement for Requirement 2, not the gate: BVA, CEG and the
    # property suite are expected to stay under 100%. --cov-fail-under=0 switches off
    # pyproject.toml's fail_under = 100 for this run only; the 100% gate still runs on the
    # full suite in the 'all' target.
    python -m pytest $File -v --cov=pricing --cov-branch --cov-report=term-missing --no-cov-on-fail --cov-fail-under=0
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
}

function Invoke-CoverageComparison {
    Write-Banner "Requirement 2: Separate Per-Suite Code Coverage Comparison"
    $pyCode = @'
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

print(f"{'Suite':<19} | {'Tests':>5} | {'Line Coverage':<18} | {'Branch Coverage':<18} | {'Missing Lines'}")
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
'@
    # Feed the snippet on stdin, not as `python -c $pyCode`: Windows PowerShell 5.1
    # (and PowerShell 7.0-7.2) pass native arguments without escaping embedded double
    # quotes, so Python received a mangled snippet ("'(' was never closed").
    $pyCode | python -
    if ($LASTEXITCODE -ne 0) { throw "Coverage comparison failed" }
}

try {
    switch ($Target) {
        "ep" {
            Invoke-SingleSuite "Requirement 1a: Equivalence Partitioning (52 tests)" "tests/test_ep.py"
        }
        "bva" {
            Invoke-SingleSuite "Requirement 1b: Boundary Value Analysis (129 tests)" "tests/test_bva.py"
        }
        "ceg" {
            Invoke-SingleSuite "Requirement 1c: Cause-Effect Graphing (17 tests)" "tests/test_ceg.py"
        }
        "mcdc" {
            Invoke-SingleSuite "Requirement 4: Modified Condition/Decision Coverage (14 tests)" "tests/test_mcdc.py"
        }
        "properties" {
            Invoke-SingleSuite "Phase 7: Hypothesis Property-Based Testing (8 properties x 200 examples)" "tests/test_properties.py"
        }
        "deep" {
            Write-Banner "Phase 7 Deep Run: Hypothesis Property-Based Testing (SLOW=1, 10,000 examples/property)"
            $prevSlow = $env:SLOW
            $env:SLOW = "1"
            try {
                python -m pytest tests/test_properties.py -v --hypothesis-show-statistics
                if ($LASTEXITCODE -ne 0) { throw "Deep property run failed" }
            } finally {
                $env:SLOW = $prevSlow
            }
        }
        "coverage" {
            Invoke-CoverageComparison
        }
        "cfg" {
            Write-Banner "Requirement 3: Control-Flow Graph, V(G)=19 & 19 Basis-Path Verifier"
            python docs/gen_cfg.py
            if ($LASTEXITCODE -ne 0) { throw "CFG verifier failed" }
        }
        "mutants" {
            Write-Banner "Requirements 5 & 6: Hand-Built Order-1 Mutants Demo (Equivalent, Killed, Surviving)"
            python mutants/run_demo.py
            if ($LASTEXITCODE -ne 0) { throw "Mutants demo failed" }
        }
        "clean" {
            Invoke-Clean
            Write-Host "[OK] Cleaned temporary test/coverage caches." -ForegroundColor Green
        }
        "all" {
            Write-Banner "STEP 1/4: Full Test Suite (220 tests) + 100% Line & Branch Coverage Gate"
            python -m pytest --cov=pricing --cov-branch --cov-fail-under=100
            if ($LASTEXITCODE -ne 0) { throw "Full test suite gate failed" }

            Invoke-CoverageComparison

            Write-Banner "STEP 3/4: Requirement 3 - Control-Flow Graph, V(G)=19 & 19 Basis-Path Verifier"
            python docs/gen_cfg.py
            if ($LASTEXITCODE -ne 0) { throw "CFG verifier failed" }

            Write-Banner "STEP 4/4: Requirements 5 & 6 - Hand-Built Mutants Live Demo"
            python mutants/run_demo.py
            if ($LASTEXITCODE -ne 0) { throw "Mutants demo failed" }

            Write-Banner "ALL TSS LAB CHECKS PASSED (220/220 TESTS, 100% LINE+BRANCH, 69 CFG CHECKS, 3/3 MUTANT CLAIMS)"
        }
    }
} finally {
    Invoke-Clean
    Pop-Location
}
