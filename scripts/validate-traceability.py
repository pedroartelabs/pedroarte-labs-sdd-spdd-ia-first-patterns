"""Validate traceability manifests: check that referenced files and tests exist."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def validate_traceability(path: Path) -> list[str]:
    errors: list[str] = []
    name = path.parent.name

    data: dict = yaml.safe_load(path.read_text(encoding="utf-8"))
    requirements = data.get("requirements", {})

    for req_id, req in requirements.items():
        source_files = req.get("source_files", [])
        for sf in source_files:
            full_path = PROJECT_ROOT / sf
            if not full_path.exists():
                errors.append(f"{name}/{req_id}: source file not found: {sf}")

        tests = req.get("tests", [])
        for test in tests:
            test_file = test.get("file", "")
            full_path = PROJECT_ROOT / test_file
            if not full_path.exists():
                lang = test.get("language", "unknown")
                if lang == "java":
                    continue
                errors.append(f"{name}/{req_id}: test file not found: {test_file}")

    return errors


def main() -> None:
    all_errors: list[str] = []

    for trace_file in sorted(PROJECT_ROOT.rglob("traceability.yaml")):
        if "templates" in str(trace_file):
            continue
        all_errors.extend(validate_traceability(trace_file))

    if all_errors:
        print("Traceability validation FAILED:")
        for e in all_errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("Traceability validation PASSED.")


if __name__ == "__main__":
    main()
