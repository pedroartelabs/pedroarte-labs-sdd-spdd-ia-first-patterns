"""Helpers for running Import Linter as a subprocess.

Import Linter is invoked as a separate process rather than through its Python
API, for two reasons that matter here:

1. **Module collisions.** Each fixture defines a package called `shopcart`.
   Linting several of them in-process would leave the first one in
   `sys.modules`, and every later fixture would silently be analysed against
   the wrong code — the tests would pass while proving nothing.
2. **It is what CI runs.** Testing the same entry point developers and workflows
   use means a change in that entry point cannot pass here and fail there.

Note that `python -m importlinter.cli` does **not** work: the module has no
`__main__` guard, so it exits 0 without linting anything. That failure mode is
silent and looks exactly like success, which is why this helper resolves the
real console script instead.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
PYTHON_EXAMPLE_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class LintResult:
    """The outcome of one Import Linter run."""

    exit_code: int
    output: str

    @property
    def broken_contracts(self) -> list[str]:
        return [
            line.removesuffix(" BROKEN").strip()
            for line in self.output.splitlines()
            if line.rstrip().endswith("BROKEN")
        ]

    @property
    def kept_contracts(self) -> list[str]:
        return [
            line.removesuffix(" KEPT").strip()
            for line in self.output.splitlines()
            if line.rstrip().endswith("KEPT")
        ]


def _lint_imports_executable() -> str:
    """Locate the `lint-imports` console script.

    Prefers the one next to the running interpreter so a virtualenv is honoured
    even when PATH points elsewhere.
    """
    candidate_dir = Path(sys.executable).parent
    for name in ("lint-imports.exe", "lint-imports"):
        candidate = candidate_dir / name
        if candidate.is_file():
            return str(candidate)
        scripts = candidate_dir / "Scripts" / name
        if scripts.is_file():
            return str(scripts)
    found = shutil.which("lint-imports")
    if found:
        return found
    pytest.fail(
        'lint-imports is not installed. Run `pip install -e ".[dev]"` in examples/python-hexagonal.'
    )


def run_import_linter(project_dir: Path, config: str = ".importlinter") -> LintResult:
    """Run Import Linter in `project_dir` and capture the result."""
    config_path = project_dir / config
    if not config_path.is_file():
        pytest.fail(f"no Import Linter config at {config_path}")

    completed = subprocess.run(  # noqa: S603 - fixed executable, no shell
        [_lint_imports_executable(), "--config", config],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    return LintResult(
        exit_code=completed.returncode,
        output=completed.stdout + completed.stderr,
    )
