# The Functions Under Test — Descriptive Reference

Every function of `pricing.py` (the module under test), what it does, the rule
an implementation could get wrong, and where each is tested. Worked examples
were computed live from the real module — open `python` and reproduce them:

```bash
python -c "import sys; sys.path.insert(0,'.'); import pricing; from decimal import Decimal as D; \
print(pricing.compute_totals(subtotal=D('100'),discount=D('10'),shipping=D('15'), \
fee_enabled=True,fee_type='percent',fee_value=D('10'),vat_enabled=True,vat_rate_percent=D('19'), \
vat_apply_to_shipping=True,vat_apply_to_fee=True))"
```

## 1. `quantize_money(value, *, rounding="half_up")` — the money-rounding primitive

- **Spec (R1–R4)**: round any decimal to exactly 2 decimal places (`0.01`), under
  one of four modes: `half_up` (default), `half_even`, `up`, `down`. Any
  unrecognized `rounding` string silently falls back to `half_up` (R3).
- **Fault site — ties**: `2.345` → `2.35` (half_up), `2.34` (half_even),
  `2.35` (up), `2.34` (down). All four are correct answers to different
  questions; confusing them is a real money bug.
- **Why tested hardest first**: every other function calls it, so its
  boundary behavior multiplies through the whole module.
- **Tested by**: EP (mode partition + fallback + error classes) · BVA (every
  tie boundary, per mode, positive/negative mirrors, `0.005` quantum) ·
  Hypothesis (`Q1` idempotence, `Q2` bounded drift ≤ `0.01` & sign preservation) ·
  indirectly by all 220 tests through every other function.

## 2. `compute_fee(*, taxable_subtotal, enabled, fee_type, fee_value, rounding="half_up")` — the fee

- **Spec (F1–F5)**: disabled (`not enabled`) or `fee_value <= 0` → `0.00`;
  `fee_type == "percent"` → `quantize_money(taxable_subtotal * fee_value / 100)`;
  otherwise (`"flat"` or any non-`"percent"` string) → `quantize_money(fee_value)`.
- **Worked examples** (from the module): flat 5 on 200 → `5.00`;
  percent 10% of 200 → `20.00`; disabled or `fee_value <= 0` → `0.00`.
- **Fault sites**: the disabled/zero short-circuit (`C1`, `C2`); the type
  switch (`C3`); percent computation landing exactly on a cent tie.
- **Tested by**: EP (enabled/type/value classes) · BVA (free-tier edge,
  value 0, `0.005`, ties) · CEG (`fee_enabled` × `fee_type` columns) ·
  MC/DC (pairs `P1–P3` for conditions `C1–C3`) · Hypothesis (`F1`).

## 3. `compute_vat(*, taxable_subtotal, shipping, fee, enabled, vat_rate_percent, apply_to_shipping, apply_to_fee, rounding="half_up")` — the VAT

- **Spec (V1–V5)**: disabled (`not enabled`) or `vat_rate_percent <= 0` → `0.00`;
  composed `base = taxable_subtotal` (+ `shipping` if `apply_to_shipping`)
  (+ `fee` if `apply_to_fee`); if `base <= 0` → `0.00`; otherwise
  `quantize_money(base * vat_rate_percent / 100)`.
- **Note on `vat_override`**: the optional override parameter lives on
  `compute_totals` (rule T6), where an active override **replaces** calling
  `compute_vat` entirely (`quantize_money(max(0, vat_override))`).
- **Fault sites**: `apply_to_shipping` / `apply_to_fee` flag combinations;
  composed `base <= 0` when a negative input offsets a positive one; rate `<= 0`
  boundary.
- **Tested by**: EP · BVA (rate 0, `0.005`, base = 0 crossings, ties) ·
  CEG (base composition & flags) · MC/DC (pairs `P4–P8` for conditions `C4–C8`).

## 4. `compute_totals(...)` — the composition

- **Spec (T1–T8), in order**:
  1. `subtotal` is quantized (`subtotal_q`, reported as-is even if negative, T1).
  2. `discount` and `shipping` contribute only when `> 0` (clamped to `0.00` if `<= 0`, T2/T4).
  3. `taxable_subtotal = max(0.00, subtotal_q - discount_q)`, quantized (T3).
  4. `fee` is computed on the **taxable** subtotal via `compute_fee` (not the pre-discount subtotal!, T5).
  5. VAT resolution (T6): `not vat_enabled` → `0.00` (even if override supplied);
     `elif vat_override is not None` → `quantize_money(max(0.00, vat_override))`
     (**replaces** rate-based VAT entirely); `else` → `compute_vat(...)`.
  6. `total = taxable_subtotal + shipping_q + fee + vat`, quantized (T7). Includes
     the defensive guard `if total < 0:` (L148, unreachable by construction since
     all four summands are `>= 0.00`).
- **The canonical walk** (from the module): subtotal 100, discount 10 →
  taxable `90.00`; shipping `15.00`; fee 10% of taxable → `9.00`;
  VAT 19% of (90+15+9)=114 → `21.66`; **total `135.66`**.
- **Fault sites**: fee on pre-discount subtotal (the classic bug); `vat_override`
  implemented as "adds" instead of "replaces"; VAT base including parts the flags
  exclude; quantization order (rounding twice vs once changes cents).
- **Tested by**: EP · BVA · CEG (all 17 decision-table columns) ·
  MC/DC (pairs `P9–P14` for conditions `C9–C14`; `C15` proven infeasible) ·
  Hypothesis (`T1–T4`, `F1`, `V1`).

## 5. `PricingBreakdown` — the record

A frozen dataclass carrying every intermediate (`subtotal, discount,
taxable_subtotal, shipping, fee, vat, total`). The CEG tests (every column) and EP's full-scenario test assert the **full
record** (all 7 fields), not just the total, and BVA's minimal-sum test pins the
`-2` exponent of all 7 fields —
that is what makes the composition tests precise about *where* a fault lands.

## Where the derivation lives

| Function | EP (52) | BVA (129) | CEG (17) | MC/DC (14) | Hypothesis (8) |
|---|---|---|---|---|---|
| `quantize_money` | `tests/test_ep.py` | `tests/test_bva.py` | *(via totals)* | *(0 decisions)* | `tests/test_properties.py` (`Q1–Q2`) |
| `compute_fee` | `tests/test_ep.py` | `tests/test_bva.py` | `tests/test_ceg.py` | `tests/test_mcdc.py` (`C1–C3`) | `tests/test_properties.py` (`F1`) |
| `compute_vat` | `tests/test_ep.py` | `tests/test_bva.py` | `tests/test_ceg.py` | `tests/test_mcdc.py` (`C4–C8`) | `tests/test_properties.py` (`T3`) |
| `compute_totals` | `tests/test_ep.py` | `tests/test_bva.py` | `tests/test_ceg.py` | `tests/test_mcdc.py` (`C9–C14`) | `tests/test_properties.py` (`T1–T4, F1, V1`) |

Full derivation documents: `docs/ep.md`, `docs/bva.md`, `docs/ceg.md`,
`docs/mcdc.md`, `docs/cfg-analysis.md`, `docs/coverage-comparison.md`,
`docs/mutants-manual.md`, `docs/mutation-analysis.md`.
The specification: `SPEC.md`. Deep end-to-end guide: `TSS_Lab_Documentation.docx`.
