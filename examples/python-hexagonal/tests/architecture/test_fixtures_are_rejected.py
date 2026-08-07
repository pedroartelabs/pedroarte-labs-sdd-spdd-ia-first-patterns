"""The negative proof: the controls must actually reject violations.

This is the most important test file in the repository, and the reason is worth
stating plainly.

Every other architecture test runs against correct code and asserts it passes.
That proves correct code passes. It says nothing about whether the control is
capable of failing — and a rule with a typo in its module pattern matches
nothing, reports KEPT forever, and lets the very violation it names sail through
review for years. Everything stays green the whole time.

So each control ships with deliberately broken code and a test asserting it is
**rejected**. The fixture list is read from the canonical policy rather than
hardcoded here, so registering a fixture without writing it — or writing one
without registering it — fails the build.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.architecture.conftest import REPO_ROOT, run_import_linter

pytestmark = pytest.mark.architecture

TESTING_POLICY = REPO_ROOT / "governance" / "policies" / "testing-policy.yaml"


def _python_fixture_cases() -> list[dict[str, Any]]:
    policy: dict[str, Any] = yaml.safe_load(TESTING_POLICY.read_text(encoding="utf-8"))
    cases: list[dict[str, Any]] = policy["negative_fixtures"]["cases"]
    return [case for case in cases if case["path"].split("/")[-1].startswith("python-")]


PYTHON_CASES = _python_fixture_cases()


def _case_id(case: dict[str, Any]) -> str:
    case_id: str = case["id"]
    return case_id


def test_the_policy_registers_python_fixtures() -> None:
    """A guard against this whole file silently testing nothing.

    If the policy key were renamed or emptied, every parametrised test below
    would collect zero cases and the suite would still be green.
    """
    assert len(PYTHON_CASES) >= 3, (
        f"expected at least 3 Python fixtures in {TESTING_POLICY.name}, found {len(PYTHON_CASES)}"
    )
    assert {case["expectation"] for case in PYTHON_CASES} == {"accepted", "rejected"}, (
        "the fixture set must contain both accepted and rejected cases; "
        "rejected-only would not prove the contracts accept valid code"
    )


@pytest.mark.parametrize("case", PYTHON_CASES, ids=_case_id)
def test_the_fixture_directory_exists(case: dict[str, Any]) -> None:
    fixture_dir = REPO_ROOT / case["path"]

    assert fixture_dir.is_dir(), (
        f"{case['id']} is registered in the testing policy but {case['path']} does not exist"
    )
    assert (fixture_dir / ".importlinter").is_file(), (
        f"{case['path']} has no .importlinter configuration"
    )


@pytest.mark.parametrize("case", PYTHON_CASES, ids=_case_id)
def test_the_control_reaches_the_expected_verdict(case: dict[str, Any]) -> None:
    fixture_dir: Path = REPO_ROOT / case["path"]

    result = run_import_linter(fixture_dir)

    if case["expectation"] == "accepted":
        assert result.broken_contracts == [], (
            f"{case['id']}: the valid fixture was rejected, so the contracts are "
            f"too strict and would block legitimate code:\n{result.output}"
        )
        assert result.exit_code == 0
    else:
        assert result.broken_contracts, (
            f"{case['id']}: the invalid fixture was ACCEPTED. The control that "
            f"should enforce {case.get('violates', '?')} is not working — this is "
            f"exactly the silent failure this test exists to catch.\n{result.output}"
        )
        assert result.exit_code != 0


@pytest.mark.parametrize(
    "case",
    [c for c in PYTHON_CASES if c["expectation"] == "rejected"],
    ids=_case_id,
)
def test_the_right_rule_fires(case: dict[str, Any]) -> None:
    """It is not enough for *something* to break.

    A fixture built to violate ARCH-001 that instead trips ARCH-006 would still
    turn the suite green while leaving ARCH-001 untested. The rule named in the
    policy must be the rule that fires.
    """
    fixture_dir = REPO_ROOT / case["path"]
    expected_rule = case["violates"]

    result = run_import_linter(fixture_dir)

    assert any(expected_rule in name for name in result.broken_contracts), (
        f"{case['id']} should violate {expected_rule}, but the broken contracts "
        f"were {result.broken_contracts}"
    )


@pytest.mark.parametrize(
    "case",
    [c for c in PYTHON_CASES if c["expectation"] == "rejected"],
    ids=_case_id,
)
def test_only_the_intended_rule_fires(case: dict[str, Any]) -> None:
    """Each invalid fixture isolates exactly one violation.

    A fixture that breaks three rules at once cannot prove any of them
    individually, and makes the failure message useless as documentation of what
    the rule actually means.
    """
    fixture_dir = REPO_ROOT / case["path"]

    result = run_import_linter(fixture_dir)

    assert len(result.broken_contracts) == 1, (
        f"{case['id']} should break exactly one contract, but broke "
        f"{len(result.broken_contracts)}: {result.broken_contracts}"
    )
