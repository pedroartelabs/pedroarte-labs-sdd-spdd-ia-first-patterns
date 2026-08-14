---
name: close-spec
description: Validate and close a specification by moving it to RELEASED
user_invocable: true
---

# /close-spec

Validate that a specification meets all closure requirements and move it to
RELEASED.

## Steps

1. Read the specification and check current status (must be VERIFIED)
2. Validate SPEC-GATE-040: traceability.yaml exists
3. Validate SPEC-GATE-041: all referenced files and tests exist
4. Verify evidence.md records actual results (no fabricated PASS)
5. Verify all acceptance criteria are covered in traceability
6. Update the specification status to RELEASED
7. Update `updated_at` in the frontmatter
8. Report the closure

## Checks

```bash
python scripts/validate-traceability.py specs/{SPEC-ID}/traceability.yaml
python scripts/validate-specs.py specs/{SPEC-ID}/spec.md
```

## Rules

- A specification can only be RELEASED from VERIFIED
- All traceability references must resolve to existing files
- Evidence must contain at least one executed command with a real result
- NOT_EXECUTED entries are acceptable if the reason is documented
