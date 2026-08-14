"""Create a new specification directory from templates."""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = PROJECT_ROOT / "specs"
TEMPLATES_DIR = SPECS_DIR / "templates"

VALID_TYPES = {"feature", "bug-fix", "hotfix", "architecture-change"}


def next_spec_id() -> str:
    year = date.today().year
    pattern = re.compile(rf"SPEC-{year}-(\d{{3}})")
    max_seq = 0
    for d in SPECS_DIR.iterdir():
        if d.is_dir():
            match = pattern.search(d.name)
            if match:
                max_seq = max(max_seq, int(match.group(1)))
    return f"SPEC-{year}-{max_seq + 1:03d}"


def kebab(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new specification")
    parser.add_argument("--name", required=True, help="Short description")
    parser.add_argument("--type", default="feature", choices=sorted(VALID_TYPES))
    args = parser.parse_args()

    spec_id = next_spec_id()
    slug = kebab(args.name)
    dir_name = f"{spec_id}-{slug}"
    spec_dir = SPECS_DIR / dir_name

    spec_dir.mkdir(parents=True, exist_ok=False)

    template_file = TEMPLATES_DIR / f"{args.type}-spec.md"
    if not template_file.exists():
        template_file = TEMPLATES_DIR / "feature-spec.md"

    today = date.today().isoformat()
    spec_content = template_file.read_text(encoding="utf-8")
    spec_content = spec_content.replace("SPEC-YYYY-NNN", spec_id)
    spec_content = spec_content.replace("YYYY-MM-DD", today)
    spec_content = spec_content.replace("{title}", args.name)
    (spec_dir / "spec.md").write_text(spec_content, encoding="utf-8")

    clarification = (TEMPLATES_DIR / "clarification-log.md").read_text(encoding="utf-8")
    clarification = clarification.replace("{SPEC-ID}", spec_id)
    (spec_dir / "clarifications.md").write_text(clarification, encoding="utf-8")

    print(f"Created {spec_dir.relative_to(PROJECT_ROOT)}")
    print(f"  spec.md          — {args.type} specification ({spec_id})")
    print(f"  clarifications.md — clarification log")
    print()
    print("Next steps:")
    print("  1. Fill in the problem statement and expected outcome")
    print("  2. Run /sdd-specify to complete the specification")
    print("  3. Run /sdd-clarify to identify ambiguities")


if __name__ == "__main__":
    main()
