# Hexagonal Architecture

Hexagonal architecture (ports and adapters) organises code around business logic
rather than technical concerns.

## Layers

| Layer | Responsibility | Depends on |
| --- | --- | --- |
| **Domain** | Business rules, aggregates, value objects, events | Nothing |
| **Application** | Use case orchestration, port definitions | Domain |
| **Adapters** | Technology translation (REST, SQL, messaging) | Domain, Application |
| **Bootstrap** | Wiring everything together | All layers |

## Core principle

Dependencies point inward. The domain is the centre and knows nothing about
frameworks, transports, or storage. Application orchestrates use cases behind
ports. Adapters implement ports and translate technology.

## Ports

A port is a contract the application declares. It describes *what* must happen,
not *how*.

- **Inbound ports** define the bounded context's offer (e.g. `CreatePixPaymentUseCase`)
- **Outbound ports** define what the use case needs (e.g. `PaymentRepository`, `Clock`)

## Adapters

An adapter implements a port using a specific technology.

- **Inbound adapters** translate external input (HTTP, CLI, events) into use case commands
- **Outbound adapters** translate port contracts into infrastructure calls (SQL, APIs, filesystem)

## Why it matters for AI-First development

An AI agent implementing a feature works within one layer at a time, with clear
boundaries on what it may import. Architecture fitness functions catch violations
deterministically, without relying on the agent's judgement.
