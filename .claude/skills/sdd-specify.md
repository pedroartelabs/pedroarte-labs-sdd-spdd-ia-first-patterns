---
name: sdd-specify
description: Fill in a specification's acceptance criteria, domain model, ports and test strategy
user_invocable: true
---

# /sdd-specify

Complete the content of an existing DRAFT specification.

## Steps

1. Read the specification at the provided path (or find the most recent DRAFT)
2. Review the problem statement and expected outcome
3. Write acceptance criteria in Given/When/Then form
4. Define the domain model: aggregates, value objects, events
5. List invariants
6. Define inbound and outbound ports
7. Write use case flows (happy path and failure paths)
8. Identify risks and mitigations
9. Draft the test strategy
10. Define the ubiquitous language
11. Validate all SPEC-GATE checks for IN_REVIEW readiness

## Rules

- Every acceptance criterion must be in Given/When/Then form
- Every port must describe a business responsibility, not a technology
- The test strategy must name specific test levels and what each proves
- Do not invent requirements — derive them from the problem statement
