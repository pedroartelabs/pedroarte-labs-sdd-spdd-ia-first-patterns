# Java hexagonal reference

Educational hexagonal architecture reference in Java 21 with Spring Boot 3.4.

**No real bank integration. No real PIX endpoint. No real personal or banking data.**

## Modules

| Module | Purpose |
| --- | --- |
| `payment-domain` | Pure domain model — no framework dependencies |
| `payment-application` | Ports and use cases |
| `payment-adapter-in-rest` | Spring REST controller |
| `payment-adapter-out-memory` | In-memory repository |
| `payment-adapter-out-persistence` | JPA repository (placeholder) |
| `payment-bootstrap` | Spring Boot composition root |
| `payment-architecture-tests` | ArchUnit tests |

## Build

```bash
./mvnw verify
```

## Architecture enforcement

Maven module boundaries enforce the hexagonal architecture at compile time.
ArchUnit tests in `payment-architecture-tests` provide additional structural
verification at test time.
