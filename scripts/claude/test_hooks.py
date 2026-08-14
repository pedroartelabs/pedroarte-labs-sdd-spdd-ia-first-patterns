"""Tests for Claude Code hooks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent


def run_hook(script: str, payload: dict) -> dict:
    """Run a hook script with the given payload and return its JSON output."""
    result = subprocess.run(
        [sys.executable, str(HOOKS_DIR / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(HOOKS_DIR),
        timeout=10,
    )
    return json.loads(result.stdout)


class TestPreToolUseGuard:
    def test_allows_safe_commands(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "python -m pytest tests/"}},
        )
        assert result["decision"] == "allow"

    def test_blocks_force_push(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}},
        )
        assert result["decision"] == "block"
        assert "THR-004" in result["reason"]

    def test_blocks_force_push_short_flag(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "git push -f origin main"}},
        )
        assert result["decision"] == "block"

    def test_blocks_hard_reset(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD~1"}},
        )
        assert result["decision"] == "block"

    def test_blocks_rm_rf_root(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}},
        )
        assert result["decision"] == "block"

    def test_blocks_drop_database(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "psql -c 'DROP DATABASE prod'"}},
        )
        assert result["decision"] == "block"

    def test_blocks_github_token_in_command(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {
                "tool_name": "Bash",
                "tool_input": {"command": "curl -H 'Authorization: token ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789'"},
            },
        )
        assert result["decision"] == "block"
        assert "SEC-001" in result["reason"]

    def test_allows_non_bash_tools(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Read", "tool_input": {"file_path": "/etc/passwd"}},
        )
        assert result["decision"] == "allow"

    def test_blocks_repo_delete(self) -> None:
        result = run_hook(
            "pre_tool_use_guard.py",
            {"tool_name": "Bash", "tool_input": {"command": "gh repo delete my-repo --yes"}},
        )
        assert result["decision"] == "block"


class TestStopQualityGate:
    def test_allows_normal_code(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "def test_foo(): assert True"}},
        )
        assert result["decision"] == "allow"

    def test_blocks_pytest_skip(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "@pytest.mark.skip\ndef test_foo(): pass"}},
        )
        assert result["decision"] == "block"
        assert "TEST-001" in result["reason"]

    def test_blocks_bare_noqa(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "import os  # noqa"}},
        )
        assert result["decision"] == "block"

    def test_allows_specific_noqa(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "import os  # noqa: F401"}},
        )
        assert result["decision"] == "allow"

    def test_blocks_bare_type_ignore(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "x = foo()  # type: ignore"}},
        )
        assert result["decision"] == "block"

    def test_allows_specific_type_ignore(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Edit", "tool_input": {"new_string": "x = foo()  # type: ignore[no-untyped-call]"}},
        )
        assert result["decision"] == "allow"

    def test_blocks_java_disabled(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Write", "tool_input": {"content": "@Disabled\nclass FooTest {}"}},
        )
        assert result["decision"] == "block"

    def test_allows_non_edit_tools(self) -> None:
        result = run_hook(
            "stop_quality_gate.py",
            {"tool_name": "Bash", "tool_input": {"command": "@pytest.mark.skip"}},
        )
        assert result["decision"] == "allow"


class TestPostEditArchitectureCheck:
    def test_warns_on_domain_edit(self) -> None:
        result = run_hook(
            "post_edit_architecture_check.py",
            {"tool_name": "Edit", "tool_input": {"file_path": "src/payment/domain/money.py", "new_string": "x = 1"}},
        )
        assert "warnings" in result
        assert any("domain" in w for w in result["warnings"])

    def test_no_warning_on_test_edit(self) -> None:
        result = run_hook(
            "post_edit_architecture_check.py",
            {"tool_name": "Edit", "tool_input": {"file_path": "tests/unit/test_money.py", "new_string": "x = 1"}},
        )
        assert result.get("warnings") is None or len(result.get("warnings", [])) == 0

    def test_no_output_for_non_edit_tools(self) -> None:
        result = run_hook(
            "post_edit_architecture_check.py",
            {"tool_name": "Bash", "tool_input": {"command": "echo hello"}},
        )
        assert "warnings" not in result or len(result.get("warnings", [])) == 0
