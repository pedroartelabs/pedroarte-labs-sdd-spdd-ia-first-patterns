---
name: implement-java-feature
description: Implement a Java feature following the SPDD prompt and hexagonal architecture
user_invocable: true
---

# /implement-java-feature

Implement a feature in the Java hexagonal reference, following the SPDD prompt.

## Steps

1. Read the SPDD prompt (`prompt.reasons.md`) and the task plan
2. Verify the specification is in IMPLEMENTING status
3. Follow the task plan phase by phase, inside-out:
   a. Domain: records, sealed types, value objects, aggregates
   b. Ports: interfaces in the application module
   c. Use case: orchestration with hand-written fakes
   d. Outbound adapters: in-memory and JPA
   e. Inbound adapter: Spring REST controller
   f. Bootstrap: Spring Boot application
   g. Architecture proofs: ArchUnit tests
4. After each phase, run:
   ```bash
   cd examples/java-hexagonal
   ./mvnw test -pl payment-{module}
   ```
5. After all phases:
   ```bash
   ./mvnw verify
   ```
6. Update task statuses in `tasks.md`
7. Record evidence in `evidence.md`

## Rules

- Stay within the change budget declared in the prompt
- Domain module has zero dependencies on frameworks
- Maven module boundaries enforce architecture at compile time
- Use JUnit 5 + AssertJ, not Mockito in domain tests
- ArchUnit tests must cover every ARCH rule
- Stop on any test failure and fix before continuing
