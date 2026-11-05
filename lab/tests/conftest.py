"""Pytest configuration for the TSS pricing lab.

Makes ``lab/`` (the directory containing ``pricing.py``) importable for the
test modules, so ``import pricing`` works regardless of the directory pytest
was invoked from. Also registers the ``ci`` (200 examples) and ``slow``
(10,000 examples) Hypothesis profiles ahead of collection so ``SLOW=1`` and
``--hypothesis-profile slow`` (or ``--hypothesis-profile=slow``) all work.
"""

import os
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent

if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))

try:
    from hypothesis import settings

    settings.register_profile("ci", max_examples=200, deadline=None)
    settings.register_profile("slow", max_examples=10_000, deadline=None)
    cli_profile = any(
        a == "--hypothesis-profile" or a.startswith("--hypothesis-profile=") for a in sys.argv
    )
    if not cli_profile:  # an explicit CLI profile wins, in either option form
        settings.load_profile("slow" if os.environ.get("SLOW", "") == "1" else "ci")
except ImportError:
    pass  # hypothesis absent: only the example-based suites run, so no profiles are needed
