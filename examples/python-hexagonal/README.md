# Python hexagonal reference — `payment`

A working implementation of the `Create PIX Payment` example, organised as
*package by bounded context first, hexagonal layers inside*.

> **Educational only.** There is no real bank integration here, no real PIX
> endpoint, and no real payment is ever made. No real personal or banking data
> appears anywhere in this repository.

## Why this exists

To show that the architecture rules in
[`governance/policies/architecture-policy.yaml`](../../governance/policies/architecture-policy.yaml)
are **executable**, not aspirational. Import Linter contracts in
[`.importlinter`](.importlinter) enforce them on every run, and the
deliberately broken fixtures in
[`architecture-fixtures/`](../../architecture-fixtures/) prove the enforcement
actually fires.

## Layout

```
src/payment/
├── domain/                     the centre — no framework, no I/O
│   ├── money.py                Money value object (Decimal, never float)
│   ├── pix_key.py              PixKey value object + masking for logs
│   ├── payment.py              Payment aggregate, PaymentId, PaymentStatus
│   ├── events.py               PaymentCreated
│   └── errors.py               domain error hierarchy
├── application/
│   ├── ports/
│   │   ├── inbound/            CreatePixPaymentUseCase + command/result
│   │   └── outbound/           PaymentRepository, Clock, IdGenerator,
│   │                           PaymentEventPublisher
│   ├── use_cases/              CreatePixPaymentService
│   └── errors.py               OutboundPortError hierarchy
├── adapters/
│   ├── inbound/rest/           FastAPI router + Pydantic DTOs
│   └── outbound/
│       ├── memory/             InMemoryPaymentRepository
│       ├── persistence/        SQLAlchemy rows + SqlPaymentRepository
│       └── system/             SystemClock, UuidIdGenerator, LoggingEventPublisher
└── bootstrap/                  the only place allowed to wire it all together
```

## Running it

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Serve the API (in-memory storage, no database needed):

```bash
uvicorn --factory payment.bootstrap.app:create_app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/payments \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-001' \
  -d '{"amount":"10.50","currency":"BRL","pix_key":"alice@example.com","pix_key_type":"EMAIL"}'
```

Repeat that call with the same `Idempotency-Key` and you get **200** with the
same `payment_id` instead of **201** with a new one.

## Verifying the architecture

```bash
lint-imports --config .importlinter    # the fitness functions
pytest tests/architecture              # including the negative fixtures
mypy                                   # strict
ruff check . && ruff format --check .
```

Or from the repository root, which runs all of the above plus coverage:

```bash
make verify-python
```

## Design decisions worth noticing

**Frameworks are real dependencies here.** FastAPI, Pydantic and SQLAlchemy are
installed on purpose. An Import Linter contract forbidding `fastapi` inside
`payment.domain` only proves something if `fastapi` is importable in the first
place — otherwise the contract passes because the package is absent, not because
the architecture is sound.

**Pydantic is banned from the domain and welcomed at the edge.** It answers "is
this parsed input well-formed?" superbly. It does not answer "is this aggregate
in a legal state after three transitions?", which is what a domain invariant
actually is.

**`Clock` and `IdGenerator` are ports.** `datetime.now()` and `uuid4()` are side
effects dressed as pure functions. Behind ports they become ordinary arguments,
and every test below asserts on exact identifiers and exact timestamps without
patching a single module.

**The in-memory repository is not a test double.** It lives in `src/`, it is
subject to the same contract suite as the SQL implementation, and it is what
lets the whole app run with no infrastructure.

**Persistence models are not domain entities.** Annotating `Payment` with
`mapped_column` and deleting `models.py` would save one file and cost the domain
its independence: a required no-arg constructor, lazy-loading proxies, identity
tied to a sequence, and an open session as a precondition for using a business
object.

## Tests

| Directory | Proves |
| --- | --- |
| `tests/unit/` | Domain invariants and use-case orchestration, with fakes |
| `tests/contract/` | Every `PaymentRepository` implementation behaves identically |
| `tests/integration/` | The SQL adapter against a real SQLite engine |
| `tests/architecture/` | Import contracts hold, and invalid fixtures are rejected |
| `tests/end_to_end/` | HTTP in, HTTP out, through the real composition root |

## Relationship to the Java reference

[`examples/java-hexagonal/`](../java-hexagonal/) implements the **same
functional intent** with the same ports and the same rules. It is not a
transliteration: Java uses records, sealed interfaces and multi-module Maven;
Python uses frozen dataclasses, `Protocol` and Import Linter. Forcing either
language to imitate the other's idioms would have taught the wrong lesson.
