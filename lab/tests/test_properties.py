"""Property-based (Hypothesis) suite for ``pricing.py`` — Phase 7.

Where the earlier suites (EP / BVA / CEG / MC/DC) sample *chosen* points,
these tests state invariants that must hold for EVERY input and let
Hypothesis search the input space for counterexamples. Each test names its
invariant (Q1..Q2, T1..T4, F1, V1) in its docstring.

Strategies: cart amounts are 2-decimal-place Decimals bounded to 1e6
(1,000,000); rates and fee values to 1e3 (1,000). The quantizer properties
Q1/Q2 draw raw amounts with up to 6 decimal places so the rounding rounds.
Every intermediate stays far below Decimal's 28-significant-digit context
- no InvalidOperation blowups. Flags are plain booleans; rounding modes and
fee types come from ``sampled_from``.
Default/deep split (this file must NOT slow the CI matrix):
  * default ("ci" profile): max_examples = 200
  * deep local pass:       SLOW=1 in the environment → max_examples = 10_000
Run the deep pass with statistics to quote the example counts:
  SLOW=1 python -m pytest tests/test_properties.py --hypothesis-show-statistics

Two switches select the deep pass, and both work: ``SLOW=1`` in the
environment, or ``--hypothesis-profile slow`` on the command line. Both
profiles ("ci" and "slow") are registered in ``tests/conftest.py``, which
is loaded early enough for ``--hypothesis-profile slow`` to find them
(verified 2026-11-05: the run passes, it does not abort). The registration
below repeats the same two profiles so this module also works when imported
on its own; an explicit ``--hypothesis-profile`` on the command line always
wins over ``SLOW`` (see the ``sys.argv`` guard below).

"""

from __future__ import annotations

import os
import sys
from decimal import (
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    Decimal,
)
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st
from pricing import MoneyRounding, PricingBreakdown, compute_totals, quantize_money

# ── profiles: CI stays at 200 examples; SLOW=1 (or the registered "slow"
# profile via --hypothesis-profile) runs the 10_000-example deep pass.
_CI_EXAMPLES = 200
_SLOW_EXAMPLES = 10_000

settings.register_profile("ci", max_examples=_CI_EXAMPLES, deadline=None)
settings.register_profile("slow", max_examples=_SLOW_EXAMPLES, deadline=None)

if "--hypothesis-profile" not in sys.argv:  # an explicit CLI profile wins
    settings.load_profile("slow" if os.environ.get("SLOW", "") == "1" else "ci")


# ── strategies ──────────────────────────────────────────────────────────────
_MONEY_QUANT = Decimal("0.01")
_CENT = Decimal("0.01")
# Bounded magnitudes: 1e6 amounts / 1e3 rates keep the largest intermediate
# (the VAT product base * rate, base <= 1.2e7, so <= 1.2e10 before / 100) at
# about 15 significant digits - safely inside the default 28-digit context.
_MAX_AMOUNT = 1_000_000
_MAX_RATE = 1_000

# Re-implementation of the money quantization used ONLY as an independent
# oracle for expected values (never calls the code under test).
_ROUNDING = {
    "half_up": ROUND_HALF_UP,
    "half_even": ROUND_HALF_EVEN,
    "up": ROUND_UP,
    "down": ROUND_DOWN,
}


def _q(value: Decimal, mode: str) -> Decimal:
    """Oracle quantizer: independent 2-dp rounding of ``value`` in ``mode``."""
    return Decimal(value).quantize(_MONEY_QUANT, rounding=_ROUNDING[mode])


# Typed with pricing's own ``MoneyRounding`` literal alias rather than bare
# ``str``: the Q-properties below pass ``mode`` straight into
# ``quantize_money(..., rounding=...)``, whose parameter is that Literal, so a
# ``str``-typed strategy is a basedpyright standard-mode error at the call.
modes: st.SearchStrategy[MoneyRounding] = st.sampled_from(("half_up", "half_even", "up", "down"))
fee_types: st.SearchStrategy[str] = st.sampled_from(("flat", "percent"))

# 2-dp cart amounts, any sign (signs exercise the <= 0 guards and the
# taxable floor at 0.00).
amounts: st.SearchStrategy[Decimal] = st.decimals(
    min_value=-_MAX_AMOUNT, max_value=_MAX_AMOUNT, places=2, allow_nan=False
)
# Rates / fee values: 2-dp, bounded, any sign (<= 0 must yield 0.00).
rates: st.SearchStrategy[Decimal] = st.decimals(
    min_value=-_MAX_RATE, max_value=_MAX_RATE, places=2, allow_nan=False
)
# Arbitrary-precision values (up to 6 fraction digits) for the quantizer
# properties, so the rounding paths actually round.
raw_amounts: st.SearchStrategy[Decimal] = st.decimals(
    min_value=-_MAX_AMOUNT, max_value=_MAX_AMOUNT, places=6, allow_nan=False
)


@st.composite
def carts(draw: st.DrawFn) -> dict[str, Any]:
    """A random cart: every kwarg ``compute_totals`` accepts, drawn freely."""
    return {
        "subtotal": draw(amounts),
        "discount": draw(amounts),
        "shipping": draw(amounts),
        "fee_enabled": draw(st.booleans()),
        "fee_type": draw(fee_types),
        "fee_value": draw(rates),
        "vat_enabled": draw(st.booleans()),
        "vat_rate_percent": draw(rates),
        "vat_apply_to_shipping": draw(st.booleans()),
        "vat_apply_to_fee": draw(st.booleans()),
        "rounding": draw(modes),
        "vat_override": draw(st.none() | amounts),
    }


def fields(bd: PricingBreakdown) -> tuple[Decimal, ...]:
    """Every money field of a breakdown, as a tuple."""
    return (
        bd.subtotal,
        bd.discount,
        bd.taxable_subtotal,
        bd.shipping,
        bd.fee,
        bd.vat,
        bd.total,
    )


# ── Q: quantize_money ───────────────────────────────────────────────────────
@given(value=raw_amounts, mode=modes)
def test_quantize_idempotent_per_mode(value: Decimal, mode: MoneyRounding) -> None:
    """Invariant Q1 — idempotence: rounding twice equals rounding once.

    For every input value and every rounding mode, quantize_money applied to
    an already-quantized result returns that result unchanged.
    """
    once = quantize_money(value, rounding=mode)
    assert quantize_money(once, rounding=mode) == once


@given(value=raw_amounts, mode=modes)
def test_quantize_cent_bound_and_sign_preserved(value: Decimal, mode: MoneyRounding) -> None:
    """Invariant Q2 — bounded drift and sign preservation.

    Quantization moves a value by at most one cent (|out - in| <= 0.01) and
    never flips its sign (positive inputs stay >= 0, negative stay <= 0) in
    every rounding mode.
    """
    out = quantize_money(value, rounding=mode)
    assert abs(out - value) <= _CENT
    if value > 0:
        assert out >= 0
    elif value < 0:
        assert out <= 0


# ── T: compute_totals ───────────────────────────────────────────────────────
@given(cart=carts())
def test_totals_conservation(cart: dict[str, Any]) -> None:
    """Invariant T1 — conservation: total == taxable + shipping + fee + vat.

    For ALL inputs (any amounts, flags, modes, optional VAT override) the
    reported total is exactly the sum of its four components — money is
    neither created nor destroyed by composition.
    """
    bd = compute_totals(**cart)
    assert bd.total == bd.taxable_subtotal + bd.shipping + bd.fee + bd.vat


@given(cart=carts())
def test_totals_discount_never_makes_taxable_negative(cart: dict[str, Any]) -> None:
    """Invariant T2 — the discount can reduce the taxable subtotal but never
    drive it negative: taxable_subtotal is floored at 0.00 and never exceeds
    ``max(subtotal, 0.00)``.

    The upper bound is the CLAMPED subtotal, not the raw one. The strategy
    draws both signs, and a negative subtotal is lifted to 0.00 by that same
    floor, so a plain ``taxable_subtotal <= subtotal`` is false by design —
    Hypothesis falsifies it at ``subtotal=-0.01`` → ``taxable_subtotal=0.00``.
    """
    bd = compute_totals(**cart)
    assert bd.taxable_subtotal >= Decimal("0.00")
    assert bd.taxable_subtotal <= max(bd.subtotal, Decimal("0.00"))


@given(cart=carts())
def test_totals_vat_non_negative(cart: dict[str, Any]) -> None:
    """Invariant T3 — VAT is never negative for any input (rate, flags,
    override included)."""
    bd = compute_totals(**cart)
    assert bd.vat >= Decimal("0.00")


@given(cart=carts())
def test_totals_every_field_two_decimal_places(cart: dict[str, Any]) -> None:
    """Invariant T4 — money shape: every field of the breakdown is quantized
    to exactly 2 decimal places (decimal exponent == -2)."""
    bd = compute_totals(**cart)
    for field in fields(bd):
        assert field.as_tuple().exponent == -2


# ── F: fee base identity ────────────────────────────────────────────────────
@given(cart=carts())
def test_fee_charged_on_taxable_subtotal(cart: dict[str, Any]) -> None:
    """Invariant F1 — the fee is computed on the TAXABLE subtotal.

    The classic fault this suite exists to catch: charging the fee on the
    pre-discount subtotal. Expected fee is recomputed independently from the
    original inputs (quantize -> subtract discount -> floor at zero), NOT
    from any breakdown field: not enabled or fee_value <= 0 → 0.00;
    percent → quantize(taxable * fee_value / 100); flat → quantize(fee_value).
    """
    mode = cart["rounding"]
    sub_q = _q(cart["subtotal"], mode)
    disc_q = _q(cart["discount"], mode) if cart["discount"] > 0 else Decimal("0.00")
    taxable = _q(max(sub_q - disc_q, Decimal("0.00")), mode)

    if not cart["fee_enabled"] or cart["fee_value"] <= 0:
        expected = Decimal("0.00")
    elif cart["fee_type"] == "percent":
        expected = _q(taxable * cart["fee_value"] / Decimal("100"), mode)
    else:
        expected = _q(cart["fee_value"], mode)

    bd = compute_totals(**cart)
    assert bd.fee == expected


# ── V: VAT override semantics ───────────────────────────────────────────────
@given(cart=carts(), vat_override=amounts, other_rate=rates)
def test_vat_override_replaces_not_adds(
    cart: dict[str, Any], vat_override: Decimal, other_rate: Decimal
) -> None:
    """Invariant V1 — a VAT override REPLACES the computed VAT, never adds.

    With VAT enabled and an override present, the reported VAT equals
    quantize(override) when the override is positive, else 0.00 — regardless
    of rate/flags. Independence is asserted directly: changing the (now
    dead) vat_rate_percent must not move the reported VAT.
    """
    # The override is injected INTO the cart dict: ``carts()`` already draws a
    # ``vat_override`` key, so passing it again as a separate keyword raises
    # "got multiple values for keyword argument" instead of testing anything.
    cart = {**cart, "vat_enabled": True, "vat_override": vat_override}
    expected = _q(vat_override, cart["rounding"]) if vat_override > 0 else Decimal("0.00")

    bd = compute_totals(**cart)
    assert bd.vat == expected

    bd_other = compute_totals(**{**cart, "vat_rate_percent": other_rate})
    assert bd_other.vat == bd.vat
