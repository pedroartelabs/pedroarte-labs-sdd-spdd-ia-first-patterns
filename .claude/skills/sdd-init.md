---
name: sdd-init
description: Create a new specification directory from the feature template
user_invocable: true
---

# /sdd-init

Create a new specification directory with all required files from templates.

## Steps

1. Ask for the specification name and type (feature, bug-fix, hotfix, architecture-change)
2. Generate the next available SPEC-ID using pattern `SPEC-{YEAR}-{SEQ}`
3. Create the directory `specs/{SPEC-ID}-{kebab-case-name}/`
4. Copy the appropriate template from `specs/templates/` as `spec.md`
5. Copy `specs/templates/clarification-log.md` as `clarifications.md`
6. Fill in the frontmatter: id, title, status=DRAFT, type, created_at, updated_at
7. Report the created files and next steps

## Rules

- Status must be DRAFT on creation
- The directory name includes the SPEC-ID and a short kebab-case description
- Never create a specification without the clarification log
