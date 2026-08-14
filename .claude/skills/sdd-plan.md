---
name: sdd-plan
description: Create the architecture plan and task decomposition for an approved specification
user_invocable: true
---

# /sdd-plan

Create the architecture plan and task plan for an APPROVED specification.

## Steps

1. Read the specification and clarification log
2. Create `architecture.md`:
   a. Identify the bounded context
   b. Draw the hexagonal diagram (Mermaid)
   c. List modules for Java and Python
   d. Define ports and their responsibilities
   e. Describe mapping strategy across boundaries
   f. List fitness functions
   g. Note required ADRs
3. Create `task-plan.md`:
   a. Decompose into phases (domain → ports → use case → adapters → bootstrap → proofs)
   b. Each task is small and individually verifiable
   c. Each task states what proves it
   d. Gates between phases
4. Create `test-plan.md`:
   a. What each test level proves
   b. Coverage targets

## Rules

- Build inside-out: domain first, HTTP last
- Every task must have a "proven by" column
- Architecture must reference specific ARCH rules
- Tasks must be ordered so each depends only on completed predecessors
