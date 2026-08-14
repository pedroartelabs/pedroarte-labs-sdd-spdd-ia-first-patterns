"""Doctor: verify the local toolchain is ready."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

CHECKS: list[tuple[str, list[str], str]] = [
    ("Python >= 3.11", [sys.executable, "--version"], "Install Python 3.11+"),
    ("pip", [sys.executable, "-m", "pip", "--version"], "Install pip"),
    ("git", ["git", "--version"], "Install git"),
    ("ruff", [sys.executable, "-m", "ruff", "--version"], "pip install ruff"),
    ("mypy", [sys.executable, "-m", "mypy", "--version"], "pip install mypy"),
    ("pytest", [sys.executable, "-m", "pytest", "--version"], "pip install pytest"),
]

OPTIONAL_CHECKS: list[tuple[str, list[str], str]] = [
    ("java", ["java", "-version"], "Install JDK 21+ for the Java reference"),
    ("mvn", ["mvn", "--version"], "Install Maven or use ./mvnw"),
    ("gh", ["gh", "--version"], "Install GitHub CLI for workflow operations"),
    ("make", ["make", "--version"], "Install make (optional, scripts work directly)"),
]


def check(name: str, cmd: list[str], fix: str, required: bool = True) -> bool:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            print(f"  ✓ {name}: {version}")
            return True
        print(f"  ✗ {name}: command failed")
    except FileNotFoundError:
        print(f"  ✗ {name}: not found")
    except subprocess.TimeoutExpired:
        print(f"  ✗ {name}: timed out")

    label = "Fix" if required else "Optional"
    print(f"    {label}: {fix}")
    return False


def main() -> None:
    print("Required tools:")
    failures = 0
    for name, cmd, fix in CHECKS:
        if not check(name, cmd, fix):
            failures += 1

    print("\nOptional tools:")
    for name, cmd, fix in OPTIONAL_CHECKS:
        check(name, cmd, fix, required=False)

    project_root = Path(__file__).resolve().parent.parent
    py_hex = project_root / "examples" / "python-hexagonal"

    print("\nProject state:")
    if (py_hex / "pyproject.toml").exists():
        print("  ✓ Python hexagonal example found")
    else:
        print("  ✗ Python hexagonal example missing")
        failures += 1

    policies = project_root / "governance" / "policies"
    policy_count = len(list(policies.glob("*.yaml"))) if policies.exists() else 0
    if policy_count >= 6:
        print(f"  ✓ Canonical policies: {policy_count} found")
    else:
        print(f"  ✗ Canonical policies: {policy_count}/6 found")
        failures += 1

    print()
    if failures:
        print(f"✗ {failures} required check(s) failed.")
        sys.exit(1)
    else:
        print("✓ All required checks passed.")


if __name__ == "__main__":
    main()
