# TSS — Software Systems Testing

Course project for **TSS (Testarea Sistemelor Software)**, FMI Master IS, 2026-2027.

## Structure

### `lab/` — Systematic Testing Lab (7 requirements)

Testing the e-commerce pricing module (fee/VAT/totals with configurable rounding):

- **Functional testing**: equivalence partitioning (52 tests), boundary value analysis (129), cause-effect graphing (17) — 198 test derivation + JUnit implementation
- **Structural testing**: control-flow graph (51 nodes, 62 edges, V(G)=19), cyclomatic complexity, basis path set, code coverage comparison (JaCoCo)
- **MC/DC**: modified condition/decision coverage with truth-table justification
- **Mutation testing**: hand-crafted mutants (equivalent, killed, surviving) + mutation scores via **mutmut** and **cosmic-ray** (176 + 226 mutants)
- **212 tests, 100% line + branch coverage**

### `course/` — Topic 4: AmbieGen (Search-Based Test Generation for Autonomous Systems)

Presentation + live demo of AmbieGen framework:

- **20-slide deck** (two presenter parts)
- **Team case study "Mountain Pass"**: new LKAS vehicle scenario (max_len 30→12, min_angle 10→25, failure threshold 5→6) with NSGA-II optimization
- Built-in robot case study reproduction
- Upstream documentation errata filed (reward_basis data/docs mismatch)
- Research notes, demo script, evidence directory

## Tech Stack

Python (pytest, pytest-cov, mutmut, cosmic-ray), NSGA-II optimization, AmbieGen framework
