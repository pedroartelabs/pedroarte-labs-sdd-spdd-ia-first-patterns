---
name: review-change
description: Review staged or committed changes against architecture, security and specification rules
user_invocable: true
---

# /review-change

Review the current changes (staged, unstaged, or a specific commit range) against
the project's governance rules.

## Steps

1. Identify what changed:
   ```bash
   git diff --name-only
   git diff --cached --name-only
   ```
2. For each changed file, determine its layer and applicable rules
3. Run the review checklist from `prompts/review/pull-request-review.md`:
   - Specification compliance
   - Architecture rules
   - Testing quality
   - Security controls
   - Code quality
4. Report findings with rule IDs and specific locations

## Rules

- This review is **advisory** (Constitution Article 6)
- Cite specific rules for every finding
- Distinguish blockers from suggestions
- Never approve — only report findings for human decision
