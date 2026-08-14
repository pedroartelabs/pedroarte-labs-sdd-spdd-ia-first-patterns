---
name: implement-python-feature
description: Implement a Python feature following the SPDD prompt and hexagonal architecture
user_invocable: true
---

# /implement-python-feature

Implement a feature in the Python hexagonal reference, following the SPDD prompt.

## Steps

1. Read the SPDD prompt (`prompt.reasons.md`) and the task plan
2. Verify the specification is in IMPLEMENTING status
3. Follow the task plan phase by phase, inside-out:
   a. Domain: value objects, aggregates, events, errors
   b. Ports: protocols in the application layer
   c. Use case: orchestration with hand-written fakes
   d. Outbound adapters: in-memory and persistence
   e. Inbound adapter: REST controller
   f. Bootstrap: composition root
   g. Architecture proofs: Import Linter contracts
4. After each phase, run:
   ```bash
   python -m pytest tests/ -v --tb=short
   python -m mypy src/ tests/ --strict
   python -m ruff check src/ tests/
   ```
5. After all phases:
   ```bash
   python -m pytest tests/ --cov=payment --cov-report=term-missing --cov-branch
   lint-imports
   ```
6. Update task statuses in `tasks.md`
7. Record evidence in `evidence.md`

## Rules

- Stay within the change budget declared in the prompt
- Domain must not import any framework
- Ports are `typing.Protocol` definitions
- Use hand-written fakes, not mocking libraries
- Tests are organised by what they prove, not by folder habit
- Stop on any test failure and fix before continuing
