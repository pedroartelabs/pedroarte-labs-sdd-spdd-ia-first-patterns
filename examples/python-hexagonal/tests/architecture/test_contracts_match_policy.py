"""The executable contracts must not drift from the canonical policy.

`governance/policies/architecture-policy.yaml` is the source of truth;
`.importlinter` is one of its executable projections. Nothing regenerates
`.importlinter` automatically, so without this test the two would drift the
first time someone adds a forbidden framework to the policy and forgets the
contract file.

The failure mode is quiet and expensive: the policy says `redis` is banned from
the domain, the documentation says so, agents are told so — and nothing checks
it. This test closes that gap.
"""

from __future__ import annotations

import configparser
from typing import Any

import pytest
import yaml

from tests.architecture.conftest import PYTHON_EXAMPLE_ROOT, REPO_ROOT

pytestmark = pytest.mark.architecture

ARCHITECTURE_POLICY = REPO_ROOT / "governance" / "policies" / "architecture-policy.yaml"
IMPORTLINTER_CONFIG = PYTHON_EXAMPLE_ROOT / ".importlinter"


@pytest.fixture(scope="module")
def policy() -> dict[str, Any]:
    loaded: dict[str, Any] = yaml.safe_load(ARCHITECTURE_POLICY.read_text(encoding="utf-8"))
    return loaded


@pytest.fixture(scope="module")
def contracts() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read(IMPORTLINTER_CONFIG, encoding="utf-8")
    return parser


def _forbidden_modules(parser: configparser.ConfigParser, section: str) -> set[str]:
    raw = parser[section].get("forbidden_modules", "")
    return {line.strip() for line in raw.splitlines() if line.strip()}


def test_the_config_files_exist() -> None:
    assert ARCHITECTURE_POLICY.is_file()
    assert IMPORTLINTER_CONFIG.is_file()


def test_every_framework_banned_from_the_domain_has_a_contract(
    policy: dict[str, Any], contracts: configparser.ConfigParser
) -> None:
    declared = set(policy["forbidden_imports"]["python"]["domain"])
    enforced = _forbidden_modules(contracts, "importlinter:contract:domain-is-framework-free")

    missing = declared - enforced

    assert not missing, (
        "these packages are forbidden in the domain by the canonical policy but "
        f"are not in the .importlinter contract, so nothing enforces them: {sorted(missing)}. "
        "Add them to the domain-is-framework-free contract."
    )


def test_every_framework_banned_from_the_application_has_a_contract(
    policy: dict[str, Any], contracts: configparser.ConfigParser
) -> None:
    declared = set(policy["forbidden_imports"]["python"]["application"])
    enforced = _forbidden_modules(contracts, "importlinter:contract:application-is-framework-free")

    missing = declared - enforced

    assert not missing, (
        "these packages are forbidden in the application layer by policy but are "
        f"not enforced by any contract: {sorted(missing)}"
    )


def test_no_contract_bans_something_the_policy_does_not(
    policy: dict[str, Any], contracts: configparser.ConfigParser
) -> None:
    """Drift runs in both directions.

    A contract stricter than the policy is not obviously wrong, but it means
    developers are blocked by a rule that is not written down anywhere they
    would look — and that is how a gate acquires a reputation for being
    arbitrary.
    """
    declared = set(policy["forbidden_imports"]["python"]["domain"])
    enforced = _forbidden_modules(contracts, "importlinter:contract:domain-is-framework-free")

    undeclared = enforced - declared

    assert not undeclared, (
        f"the .importlinter contract bans {sorted(undeclared)} but the canonical "
        "policy does not mention them. Add them to "
        "governance/policies/architecture-policy.yaml so the rule is discoverable."
    )


def test_every_layer_in_the_policy_appears_in_the_layers_contract(
    policy: dict[str, Any], contracts: configparser.ConfigParser
) -> None:
    layers_raw = contracts["importlinter:contract:layers"]["layers"]
    contract_text = layers_raw.replace(":", " ")

    for layer in policy["layers"]:
        module = layer.get("python_module_pattern")
        if not module:
            continue
        assert module in contract_text, (
            f"layer {layer['id']} maps to module {module}, which does not appear "
            "in the .importlinter layers contract"
        )


def test_contract_names_carry_their_rule_ids(contracts: configparser.ConfigParser) -> None:
    """A failure message should name the rule a developer can look up."""
    contract_sections = [s for s in contracts.sections() if s.startswith("importlinter:contract:")]

    assert contract_sections, "no contracts are defined"

    for section in contract_sections:
        name = contracts[section]["name"]
        assert "ARCH-" in name, (
            f"contract {section!r} is named {name!r} and references no ARCH rule id; "
            "a developer who hits it has nothing to look up"
        )


def test_forbidden_dependencies_in_policy_are_covered_by_contracts(
    policy: dict[str, Any], contracts: configparser.ConfigParser
) -> None:
    """Adapter isolation must be enforced, not merely declared."""
    adapter_rules = [
        entry for entry in policy["forbidden_dependencies"] if entry["from"].startswith("adapter_")
    ]
    assert adapter_rules, "the policy declares no adapter isolation rules"

    independence = contracts["importlinter:contract:adapter-independence"]
    modules = {line.strip() for line in independence["modules"].splitlines() if line.strip()}

    assert modules == {"payment.adapters.inbound", "payment.adapters.outbound"}, (
        "the adapter independence contract must cover both adapter packages; "
        f"it currently covers {sorted(modules)}"
    )
