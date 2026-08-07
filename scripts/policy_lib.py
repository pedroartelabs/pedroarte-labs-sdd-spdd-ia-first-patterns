"""Canonical policy loading and agent-instruction rendering.

This module is the engine behind `generate-agent-rules.py` and
`check-generated-rule-drift.py`. Both CLI entry points import it so that the
generator and the drift checker can never disagree about what "correct" means:
there is exactly one rendering implementation.

Design notes
------------
* `governance/policies/*.yaml` is the only source of truth. Nothing here invents
  a rule; everything is projected from the YAML.
* Rendering must be deterministic. PyYAML preserves mapping insertion order on
  Python 3.7+, and every place where we iterate a set we sort it first.
* Every generated file carries a checksum of the canonical inputs. A human edit
  changes the body, a policy edit changes the checksum; the drift checker
  catches both.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    sys.stderr.write(
        "error: PyYAML is required.\n"
        "       Install it with: python -m pip install -r scripts/requirements.txt\n"
    )
    raise SystemExit(2) from None

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = REPO_ROOT / "governance" / "policies"

POLICY_FILES = (
    "architecture-policy.yaml",
    "ai-first-policy.yaml",
    "specification-policy.yaml",
    "testing-policy.yaml",
    "security-policy.yaml",
    "quality-gates.yaml",
)

DO_NOT_EDIT = "GENERATED FILE — DO NOT EDIT DIRECTLY"


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Policies:
    """The canonical policy set, plus a checksum over its raw bytes."""

    architecture: dict[str, Any]
    ai_first: dict[str, Any]
    specification: dict[str, Any]
    testing: dict[str, Any]
    security: dict[str, Any]
    gates: dict[str, Any]
    checksum: str


def load_policies(policy_dir: Path = POLICY_DIR) -> Policies:
    """Read every canonical policy file and checksum the raw bytes.

    The checksum is taken over the bytes on disk rather than over the parsed
    structure: a comment change in a policy is still a change a reviewer should
    see reflected downstream.
    """
    digest = hashlib.sha256()
    parsed: dict[str, dict[str, Any]] = {}

    for name in POLICY_FILES:
        path = policy_dir / name
        if not path.is_file():
            raise SystemExit(f"error: missing canonical policy file: {path}")
        raw = path.read_bytes()
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(raw.replace(b"\r\n", b"\n"))
        parsed[name] = yaml.safe_load(raw.decode("utf-8")) or {}

    return Policies(
        architecture=parsed["architecture-policy.yaml"],
        ai_first=parsed["ai-first-policy.yaml"],
        specification=parsed["specification-policy.yaml"],
        testing=parsed["testing-policy.yaml"],
        security=parsed["security-policy.yaml"],
        gates=parsed["quality-gates.yaml"],
        checksum=digest.hexdigest(),
    )


# --------------------------------------------------------------------------
# Header helpers
# --------------------------------------------------------------------------


def _markdown_header(policies: Policies) -> str:
    return (
        f"<!-- {DO_NOT_EDIT}\n"
        f"     Source: governance/policies/\n"
        f"     Regenerate with: make generate-agent-rules\n"
        f"     Policy checksum: sha256:{policies.checksum}\n"
        f"-->\n"
    )


def _bullet(items: list[str], indent: str = "") -> str:
    return "".join(f"{indent}- {item}\n" for item in items)


def _layer_table(policies: Policies) -> str:
    rows = ["| Layer | May depend on | Java package | Python module |",
            "| --- | --- | --- | --- |"]
    for layer in policies.architecture["layers"]:
        deps = ", ".join(layer["may_depend_on"]) or "*(nothing)*"
        rows.append(
            f"| `{layer['id']}` | {deps} | `{layer.get('java_package_pattern', '—')}` "
            f"| `{layer.get('python_module_pattern', '—')}` |"
        )
    return "\n".join(rows) + "\n"


def _forbidden_dependency_lines(policies: Policies) -> list[str]:
    lines = []
    for entry in policies.architecture["forbidden_dependencies"]:
        targets = ", ".join(f"`{t}`" for t in entry["to"])
        lines.append(f"`{entry['from']}` must not depend on {targets} — {entry.get('reason', '')}".strip(" —"))
    return lines


def _arch_rule_lines(policies: Policies, language: str | None = None) -> list[str]:
    lines = []
    for rule in policies.architecture["rules"]:
        if language and language not in rule["applies_to"]:
            continue
        lines.append(
            f"**{rule['id']}** ({rule['severity']}) — {rule['title']}. "
            f"Enforced by: {', '.join(rule['enforced_by'])}."
        )
    return lines


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------


def render_claude_md(policies: Policies) -> str:
    arch = policies.architecture
    spec = policies.specification
    ai = policies.ai_first
    gates = policies.gates

    steps = "\n".join(
        f"{s['step']}. {s['name']}" + (f" — `{s['skill']}`" if s.get("skill") else "")
        for s in spec["golden_path"]
    )

    blocking_gates = [g for g in gates["gates"] if g["severity"] == "blocker"]

    return f"""{_markdown_header(policies)}
# CLAUDE.md

## Mission

This repository is a public reference for **AI-First software delivery under
governance**: SDD, SPDD, Hexagonal Architecture, architecture tests, Claude Code
Skills, and deterministic quality gates for Java and Python.

{ai['principle']}

AI-First is **not** {", ".join(x[0].lower() + x[1:] for x in ai['not_equal_to'][1:])}.

## Canonical source of rules

Every rule below is projected from `governance/policies/`. That directory is the
single source of truth.

- Do **not** edit `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`,
  `.github/copilot-instructions.md` or `.cursor/rules/*.mdc` by hand.
- Change the YAML policy, then run `make generate-agent-rules`.
- `make check-rule-drift` fails the build when a generated file was hand-edited
  or when a policy changed without regeneration.

## Core commands

```bash
make doctor                 # verify the local toolchain
make setup                  # install dev dependencies
make generate-agent-rules   # regenerate agent instruction files from policy
make check-rule-drift       # fail if generated files drifted from policy
make spec-new NAME="..." TYPE=feature
make validate-specs         # SDD lifecycle and schema validation
make validate-prompts       # SPDD REASONS validation
make validate-traceability  # requirement -> code -> test -> evidence
make verify-architecture    # ArchUnit + Import Linter + negative fixtures
make verify-java
make verify-python
make verify-security
make verify-docs
make verify                 # everything that must pass before a pull request
```

## Mandatory workflow

No production code without an approved specification. The golden path:

{steps}

Skills implement these steps. Prefer `/sdd-specify`, `/sdd-clarify`, `/sdd-plan`,
`/spdd-generate`, `/implement-java-feature`, `/implement-python-feature`,
`/architecture-check`, `/review-change`, `/create-adr`, `/close-spec` over
improvising the process.

## Architecture rules (non-negotiable)

{arch['summary']}

{_layer_table(policies)}
{_bullet(_forbidden_dependency_lines(policies))}
{_bullet(_arch_rule_lines(policies))}
### Forbidden imports in the domain

- **Java:** {", ".join(f"`{p}`" for p in arch['forbidden_imports']['java']['domain'])}
- **Python:** {", ".join(f"`{p}`" for p in arch['forbidden_imports']['python']['domain'])}

A deliberate deviation requires an ADR with owner, justification and review date
(`{arch['exceptions_register']}`).

## Definition of Done

A change is done only when all of the following are true and **proven**:

{_bullet([
    "The specification exists, is approved, and matches what was built.",
    "The SPDD prompt is versioned and linked to that specification.",
    "Implementation is incremental and stays inside the declared file scope.",
    "Unit, contract, integration and architecture tests pass.",
    "Coverage thresholds hold (domain/application 95% line, repository 85%).",
    "No quality gate was weakened, no test disabled, no rule suppressed.",
    "Traceability is updated.",
    "Security checks pass and no secret was introduced.",
    "Evidence is recorded: the exact commands run and their real results.",
])}
## Evidence discipline

Never report a command as passing unless it actually ran and actually passed.
When something could not be executed, say so explicitly and record it as
`NOT_EXECUTED` with the reason. A confident summary is not evidence.

There are {len(blocking_gates)} blocking quality gates; see
`docs/reference/quality-gates.md` for the full catalogue.

## Safeguards

{_bullet(ai['spdd']['mandatory_safeguards'])}
## AI is not the approver

{ai['ai_review']['rationale']}
"""


def render_agents_md(policies: Policies) -> str:
    arch = policies.architecture
    spec = policies.specification
    ai = policies.ai_first

    reasons = "\n".join(
        f"- **{s['key'].rstrip('2')} — {s['name']}**: {'; '.join(s['must_answer'])}"
        for s in ai["spdd"]["sections"]
    )

    return f"""{_markdown_header(policies)}
# AGENTS.md

Tool-agnostic instructions for any coding agent operating in this repository.
Claude Code reads `CLAUDE.md`; other agents read this file. Both are generated
from `governance/policies/`.

## Ground rules

1. **No production code without an approved specification.** Production paths are
   {", ".join(f"`{p}`" for p in spec['production_code_paths']['include'])}.
2. **The prompt derives from the specification**, never replaces it.
3. **Prompts are versioned artifacts** with an id, a linked spec, constraints,
   stop conditions and a change log.
4. **Dependencies point inward.** {arch['summary']}
5. **Architecture is executable.** Every important rule has an automated check.
6. **AI does not approve alone.** {ai['ai_review']['rationale']}
7. **Evidence before completion.** Record the command and its real result.

## Structured prompts: the REASONS model

{reasons}

## Architecture contract

{_layer_table(policies)}
{_bullet(_forbidden_dependency_lines(policies))}
### Rules

{_bullet(_arch_rule_lines(policies))}
## Safeguards every agent must honour

{_bullet(ai['spdd']['mandatory_safeguards'])}
## Roles an agent may take

Allowed: {", ".join(ai['agent_roles']['allowed'])}.

Forbidden: {", ".join(ai['agent_roles']['forbidden'])}.

## Verification commands

```bash
make verify-architecture
make verify-java
make verify-python
make verify
```
"""


def render_rule_architecture(policies: Policies) -> str:
    arch = policies.architecture
    return f"""{_markdown_header(policies)}
# Architecture rules

{arch['summary']}

Strategy: `{arch['strategy']}`.

## Layers

{_layer_table(policies)}
## Forbidden dependencies

{_bullet(_forbidden_dependency_lines(policies))}
## Enforced rules

{_bullet(_arch_rule_lines(policies))}
## Naming conventions

{_bullet([
    f"**{n['id']}** — {n['rule']}"
    + (f" Forbidden substrings: {', '.join(n['forbidden_substrings'])}." if n.get('forbidden_substrings') else "")
    for n in arch.get('naming_conventions', [])
])}
## Exceptions

Deliberate deviations are recorded in `{arch['exceptions_register']}` and require
an ADR, an owner, a risk statement and an expiry date. No exception is permanent.
"""


def render_rule_java(policies: Policies) -> str:
    arch = policies.architecture
    forbidden = arch["forbidden_imports"]["java"]
    return f"""{_markdown_header(policies)}
# Java rules

## Module boundaries

The Java reference is multi-module on purpose: Maven refuses a dependency that
the architecture forbids, so violations fail at compile time rather than at
review time.

```
payment-domain                  -> depends on nothing
payment-application             -> payment-domain
payment-adapter-in-rest         -> payment-application, payment-domain
payment-adapter-out-memory      -> payment-application, payment-domain
payment-adapter-out-persistence -> payment-application, payment-domain
payment-bootstrap               -> whatever composition requires
payment-architecture-tests      -> inspects the modules above
```

## Forbidden imports

- **Domain:** {", ".join(f"`{p}`" for p in forbidden['domain'])}
- **Application:** {", ".join(f"`{p}`" for p in forbidden['application'])}

Frameworks are welcome in adapters and bootstrap. They are never welcome in
`payment-domain`. A domain entity is not a JPA entity and carries no Jackson,
Spring or persistence annotation.

## Rules that apply to Java

{_bullet(_arch_rule_lines(policies, "java"))}
## Testing

- JUnit 5 + AssertJ for behaviour, ArchUnit for structure.
- Prefer hand-written fakes over mocks for outbound ports; a fake that
  implements the port is also a contract test subject.
- JaCoCo enforces coverage; PIT runs mutation testing in a separate job.
- Every architecture rule ships with a negative fixture proving it fires.
"""


def render_rule_python(policies: Policies) -> str:
    arch = policies.architecture
    forbidden = arch["forbidden_imports"]["python"]
    return f"""{_markdown_header(policies)}
# Python rules

## Layout

`src` layout, one package per bounded context:

```
src/payment/
├── domain/
├── application/
│   ├── ports/{{inbound,outbound}}/
│   └── use_cases/
├── adapters/{{inbound,outbound}}/
└── bootstrap/
```

## Forbidden imports

- **Domain:** {", ".join(f"`{p}`" for p in forbidden['domain'])}
- **Application:** {", ".join(f"`{p}`" for p in forbidden['application'])}

Note that `pydantic` is forbidden in the domain deliberately. It is an excellent
transport-validation library and a poor domain model: validation-on-construction
is not the same thing as an invariant that the type system and the aggregate
enforce together.

## Rules that apply to Python

{_bullet(_arch_rule_lines(policies, "python"))}
## Typing

{_bullet([
    "Public APIs carry explicit type annotations.",
    "Ports are `typing.Protocol` definitions in the application layer.",
    "Domain models are plain dataclasses (frozen where they are value objects).",
    "No blanket `Any`; no bare `# type: ignore` without a written reason.",
    "`None` is handled explicitly, never by accident.",
    "DTO conversion happens in adapters, never in the domain.",
])}
## Tooling

Ruff (lint + format), mypy (strict), Import Linter (architecture), pytest with
pytest-cov, Hypothesis where property tests earn their keep, Bandit for security.
"""


def render_rule_specifications(policies: Policies) -> str:
    spec = policies.specification
    states = "\n".join(f"- **{s['id']}** — {s['description']}" for s in spec["lifecycle"]["states"])
    transitions = "\n".join(
        f"- `{t['from']}` → {', '.join(f'`{x}`' for x in t['to']) if t['to'] else '*(terminal)*'}"
        for t in spec["lifecycle"]["transitions"]
    )
    entry = []
    for state, reqs in spec["lifecycle"]["entry_requirements"].items():
        entry.append(f"\n### Entering `{state}`\n")
        entry.extend(f"- **{r['id']}** — fails when {r['message']}" for r in reqs)
    return f"""{_markdown_header(policies)}
# Specification rules

{spec['summary']}

## Identifier

Pattern: `{spec['identifier']['pattern']}` — for example
{", ".join(f"`{e}`" for e in spec['identifier']['examples'])}.

## Lifecycle

{states}

## Allowed transitions

{transitions}

## Entry requirements
{chr(10).join(entry)}

## Required frontmatter

{", ".join(f"`{f}`" for f in spec['frontmatter']['required_fields'])}.

Optional: {", ".join(f"`{f}`" for f in spec['frontmatter']['optional_fields'])}.

## Pull request linkage

A pull request touching production paths must reference an approved
`SPEC-ID` matching `{spec['pull_request']['spec_id_pattern']}`, and once the
specification is `IMPLEMENTING` it must also reference a `PROMPT-ID` matching
`{spec['pull_request']['prompt_id_pattern']}`.
"""


def render_rule_testing(policies: Policies) -> str:
    testing = policies.testing
    levels = "\n".join(
        f"- **{lv['title']}** — {', '.join(lv['characteristics'])}. Focus: {', '.join(lv['focus'])}."
        for lv in testing["levels"]
    )
    thresholds = "\n".join(
        f"- `{t['scope']}`: line ≥ {t['line']}%, branch ≥ {t['branch']}%"
        + (" (blocking)" if t.get("blocking") else "")
        for t in testing["coverage"]["thresholds"]
    )
    forbidden = "\n".join(f"- **{f['id']}** ({f['severity']}) — {f['rule']}" for f in testing["forbidden"])
    fixtures = "\n".join(
        f"- `{c['path']}` → expected **{c['expectation']}**"
        + (f" (violates {c['violates']})" if c.get("violates") else "")
        for c in testing["negative_fixtures"]["cases"]
    )
    return f"""{_markdown_header(policies)}
# Testing rules

{testing['summary']}

## Levels

{levels}

## Coverage

{thresholds}

{testing['coverage']['rules'][0]}
{testing['coverage']['rules'][1]}

## Mutation testing

{testing['mutation_testing']['rationale']}
Java: {testing['mutation_testing']['java_tool']}. Python: {testing['mutation_testing']['python_tool']}.
Runs as a {testing['mutation_testing']['execution']}.

## Forbidden

{forbidden}

## Negative fixtures

{testing['negative_fixtures']['description']}

{fixtures}
"""


def render_rule_security(policies: Policies) -> str:
    sec = policies.security
    threats = "\n".join(
        f"- **{t['id']}** — {t['threat']}\n  - Impact: {t['impact']}\n"
        + "".join(f"  - Control: {c}\n" for c in t["controls"])
        for t in sec["threat_model"]
    )
    controls = "\n".join(
        f"- **{c['id']}** ({c['severity']}) — {c['rule']} Enforced by: {', '.join(c['enforced_by'])}."
        for c in sec["code_controls"]
    )
    return f"""{_markdown_header(policies)}
# Security rules

{sec['summary']}

## Threat model for the AI-First process

{threats}

## Code controls

{controls}

## Destructive commands an agent must never run

{_bullet(sec['destructive_commands']['deny'])}
## Secret patterns blocked before they reach disk

{_bullet([f"`{p['name']}`" for p in sec['secret_patterns']['patterns']])}
Never commit a real credential. `.env.example` carries fictitious values only.
The PIX example is educational: no real bank integration, no real personal or
banking data anywhere in this repository.
"""


def render_copilot_instructions(policies: Policies) -> str:
    arch = policies.architecture
    spec = policies.specification
    return f"""{_markdown_header(policies)}
# GitHub Copilot instructions

This repository enforces AI-First delivery under governance. The canonical rules
live in `governance/policies/`; this file is generated from them.

## Before writing code

- A change to production code requires an approved specification under `specs/`.
- Production paths: {", ".join(f"`{p}`" for p in spec['production_code_paths']['include'])}.
- The implementation follows a versioned SPDD prompt (`prompt.reasons.md`).

## Architecture

{arch['summary']}

{_layer_table(policies)}
{_bullet(_forbidden_dependency_lines(policies))}
## Never do this

{_bullet([
    "Import a framework into `domain` (Java: Spring, JPA, Hibernate, Jackson; Python: FastAPI, SQLAlchemy, Pydantic).",
    "Make an inbound adapter call an outbound adapter directly.",
    "Put a business rule in a controller or a repository implementation.",
    "Use an ORM entity or a transport DTO as a domain model.",
    "Disable a test or weaken a quality gate to make a build pass.",
    "Introduce a dependency cycle.",
    "Commit a secret, a token or real personal data.",
])}
## Always do this

{_bullet([
    "Declare an outbound port in `application/ports/outbound` before touching infrastructure.",
    "Keep ports free of technology names (no `Jpa`, `Rest`, `Kafka`, `Sql` in a port name).",
    "Translate technical exceptions at the adapter boundary.",
    "Abstract clock, randomness and id generation behind ports when they affect business rules.",
    "Write the test with the code, at the level that actually proves the behaviour.",
    "Record the exact verification commands you ran and their real results.",
])}
Run `make verify` before proposing a change.
"""


def _cursor_frontmatter(description: str, globs: str, always: bool) -> str:
    return f"---\ndescription: {description}\nglobs: {globs}\nalwaysApply: {str(always).lower()}\n---\n\n"


def render_cursor_hexagonal(policies: Policies) -> str:
    arch = policies.architecture
    return (
        _cursor_frontmatter(
            "Hexagonal architecture boundaries: dependencies point inward, adapters never call adapters.",
            "**/*.java,**/*.py",
            True,
        )
        + f"""{_markdown_header(policies)}
# Hexagonal architecture

{arch['summary']}

{_layer_table(policies)}
{_bullet(_forbidden_dependency_lines(policies))}
{_bullet(_arch_rule_lines(policies))}"""
    )


def render_cursor_sdd_spdd(policies: Policies) -> str:
    spec = policies.specification
    ai = policies.ai_first
    return (
        _cursor_frontmatter(
            "SDD and SPDD process: specification first, versioned structured prompt, evidence before completion.",
            "specs/**,prompts/**",
            False,
        )
        + f"""{_markdown_header(policies)}
# SDD and SPDD

{spec['summary']}

## Lifecycle

{" → ".join(s['id'] for s in spec['lifecycle']['states'][:6])}

## REASONS

{_bullet([f"**{s['key'].rstrip('2')} — {s['name']}**: {'; '.join(s['must_answer'][:3])}" for s in ai['spdd']['sections']])}
## Safeguards

{_bullet(ai['spdd']['mandatory_safeguards'])}"""
    )


def render_cursor_java(policies: Policies) -> str:
    forbidden = policies.architecture["forbidden_imports"]["java"]
    return (
        _cursor_frontmatter(
            "Java module boundaries and forbidden framework imports in the domain.",
            "**/*.java",
            False,
        )
        + f"""{_markdown_header(policies)}
# Java

Multi-module Maven enforces boundaries at compile time.

- `payment-domain` depends on nothing.
- `payment-application` depends only on `payment-domain`.
- Adapters depend on application and domain, never on each other.
- Only `payment-bootstrap` performs composition.

Forbidden in the domain: {", ".join(f"`{p}`" for p in forbidden['domain'])}.

Forbidden in the application: {", ".join(f"`{p}`" for p in forbidden['application'])}.

JUnit 5 + AssertJ for behaviour, ArchUnit for structure, JaCoCo for coverage."""
    )


def render_cursor_python(policies: Policies) -> str:
    forbidden = policies.architecture["forbidden_imports"]["python"]
    return (
        _cursor_frontmatter(
            "Python src layout, Protocol-based ports, forbidden framework imports in the domain.",
            "**/*.py",
            False,
        )
        + f"""{_markdown_header(policies)}
# Python

`src` layout, one package per bounded context, hexagonal layers inside.

Forbidden in the domain: {", ".join(f"`{p}`" for p in forbidden['domain'])}.

Forbidden in the application: {", ".join(f"`{p}`" for p in forbidden['application'])}.

- Ports are `typing.Protocol` definitions in `application/ports`.
- Domain models are plain dataclasses; value objects are frozen.
- No blanket `Any`, no unexplained `# type: ignore`.
- Import Linter contracts in `.importlinter` are the executable form of these rules."""
    )


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

Renderer = Callable[[Policies], str]

GENERATED_FILES: dict[str, Renderer] = {
    "CLAUDE.md": render_claude_md,
    "AGENTS.md": render_agents_md,
    ".claude/rules/architecture.md": render_rule_architecture,
    ".claude/rules/java.md": render_rule_java,
    ".claude/rules/python.md": render_rule_python,
    ".claude/rules/specifications.md": render_rule_specifications,
    ".claude/rules/testing.md": render_rule_testing,
    ".claude/rules/security.md": render_rule_security,
    ".github/copilot-instructions.md": render_copilot_instructions,
    ".cursor/rules/hexagonal-architecture.mdc": render_cursor_hexagonal,
    ".cursor/rules/sdd-spdd.mdc": render_cursor_sdd_spdd,
    ".cursor/rules/java.mdc": render_cursor_java,
    ".cursor/rules/python.mdc": render_cursor_python,
}


def render_all(policies: Policies) -> dict[str, str]:
    """Render every generated file, normalised to LF endings."""
    return {
        rel: renderer(policies).replace("\r\n", "\n")
        for rel, renderer in GENERATED_FILES.items()
    }


def read_existing(repo_root: Path, rel: str) -> str | None:
    path = repo_root / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")
