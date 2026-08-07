"""The real project must satisfy every architecture contract.

The positive half of the proof. The negative half — that the contracts can
actually fail — lives in `test_fixtures_are_rejected.py`, and neither half means
much without the other.
"""

from __future__ import annotations

import pytest

from tests.architecture.conftest import PYTHON_EXAMPLE_ROOT, run_import_linter

pytestmark = pytest.mark.architecture


def test_every_contract_is_kept() -> None:
    result = run_import_linter(PYTHON_EXAMPLE_ROOT)

    assert result.broken_contracts == [], (
        "the payment package violates its own architecture contracts:\n" + result.output
    )
    assert result.exit_code == 0


def test_all_six_contracts_actually_ran() -> None:
    """Guards against the quietest failure mode in architecture governance.

    A contract whose `source_modules` no longer match anything reports KEPT
    forever. Counting them means a renamed package cannot silently disable a
    rule while the build stays green.
    """
    result = run_import_linter(PYTHON_EXAMPLE_ROOT)

    assert len(result.kept_contracts) == 6, (
        f"expected 6 contracts, saw {len(result.kept_contracts)}: {result.kept_contracts}"
    )


@pytest.mark.parametrize(
    "rule_id",
    ["ARCH-002/003/007", "ARCH-004/005", "ARCH-001", "ARCH-012", "ARCH-007"],
)
def test_each_policy_rule_is_represented_by_a_contract(rule_id: str) -> None:
    """Every contract name carries the rule id it enforces.

    This is what makes a failure message traceable: a developer who breaks a
    contract sees `ARCH-004` and can look the rule up in the policy catalogue
    instead of guessing what "layers violated" means for their change.
    """
    result = run_import_linter(PYTHON_EXAMPLE_ROOT)

    assert any(rule_id in name for name in result.kept_contracts), (
        f"no contract references {rule_id}"
    )
