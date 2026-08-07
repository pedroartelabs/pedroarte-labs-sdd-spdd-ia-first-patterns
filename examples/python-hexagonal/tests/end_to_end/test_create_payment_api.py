"""End-to-end: HTTP in, HTTP out, through the real composition root.

Few, representative and stable. These go through the actual `create_app`
factory, the actual controller, the actual use case and the actual aggregate —
only the clock and the id generator are replaced, so responses are assertable
by exact value.

Replacing exactly two adapters and keeping the rest of the real wiring is the
point. A test that builds the object graph by hand slowly stops resembling
production, and then stops catching production's bugs.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from payment.bootstrap.app import create_app
from tests.support import (
    FIXED_INSTANT,
    ID_ONE,
    ID_TWO,
    FailingPaymentRepository,
    FixedClock,
    RecordingEventPublisher,
    SequentialIdGenerator,
)

pytestmark = pytest.mark.e2e

VALID_BODY = {
    "amount": "10.50",
    "currency": "BRL",
    "pix_key": "alice@example.com",
    "pix_key_type": "EMAIL",
}


@pytest.fixture
def events() -> RecordingEventPublisher:
    return RecordingEventPublisher()


@pytest.fixture
def client(events: RecordingEventPublisher) -> Iterator[TestClient]:
    app = create_app(
        payments=InMemoryPaymentRepository(),
        clock=FixedClock(),
        id_generator=SequentialIdGenerator(ID_ONE, ID_TWO),
        event_publisher=events,
    )
    with TestClient(app) as test_client:
        yield test_client


class TestHealth:
    def test_reports_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreatePayment:
    def test_creates_a_payment(self, client: TestClient) -> None:
        response = client.post(
            "/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-001"}
        )

        assert response.status_code == 201
        body = response.json()
        assert body["payment_id"] == ID_ONE
        assert body["status"] == "PENDING"
        assert body["amount"] == "10.50"
        assert body["currency"] == "BRL"

    def test_the_timestamp_comes_from_the_injected_clock(self, client: TestClient) -> None:
        response = client.post(
            "/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-001"}
        )

        assert response.json()["created_at"].startswith(FIXED_INSTANT.date().isoformat())

    def test_the_domain_event_reaches_the_publisher(
        self, client: TestClient, events: RecordingEventPublisher
    ) -> None:
        client.post("/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-001"})

        assert len(events.published) == 1

    def test_accepts_a_description(self, client: TestClient) -> None:
        response = client.post(
            "/payments",
            json={**VALID_BODY, "description": "rent for March"},
            headers={"Idempotency-Key": "idem-001"},
        )

        assert response.status_code == 201


class TestIdempotency:
    def test_a_replay_returns_200_not_201(self, client: TestClient) -> None:
        headers = {"Idempotency-Key": "idem-retry"}

        first = client.post("/payments", json=VALID_BODY, headers=headers)
        second = client.post("/payments", json=VALID_BODY, headers=headers)

        # 201 on a replay would be a lie: nothing was created. The status code
        # is the honest signal a client needs to distinguish the two.
        assert first.status_code == 201
        assert second.status_code == 200
        assert second.json()["payment_id"] == first.json()["payment_id"]

    def test_a_replay_publishes_nothing_new(
        self, client: TestClient, events: RecordingEventPublisher
    ) -> None:
        headers = {"Idempotency-Key": "idem-retry"}

        client.post("/payments", json=VALID_BODY, headers=headers)
        client.post("/payments", json=VALID_BODY, headers=headers)

        assert len(events.published) == 1

    def test_distinct_keys_create_distinct_payments(self, client: TestClient) -> None:
        first = client.post("/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-1"})
        second = client.post("/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-2"})

        assert first.json()["payment_id"] != second.json()["payment_id"]

    def test_the_idempotency_key_is_required(self, client: TestClient) -> None:
        response = client.post("/payments", json=VALID_BODY)

        assert response.status_code == 422


class TestValidation:
    """Two different layers reject bad input, and both must reach the client."""

    def test_pydantic_rejects_a_non_positive_amount(self, client: TestClient) -> None:
        response = client.post(
            "/payments",
            json={**VALID_BODY, "amount": "0"},
            headers={"Idempotency-Key": "idem-001"},
        )

        assert response.status_code == 422

    def test_pydantic_rejects_an_unknown_field(self, client: TestClient) -> None:
        # `extra="forbid"`: a client sending `ammount` should be told, not
        # silently have the field ignored and the payment created wrong.
        response = client.post(
            "/payments",
            json={**VALID_BODY, "ammount": "10.50"},
            headers={"Idempotency-Key": "idem-001"},
        )

        assert response.status_code == 422

    def test_the_domain_rejects_an_unsupported_currency(self, client: TestClient) -> None:
        # Passes Pydantic (three characters) and is caught by Money.
        response = client.post(
            "/payments",
            json={**VALID_BODY, "currency": "XYZ"},
            headers={"Idempotency-Key": "idem-001"},
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "InvalidMoneyError"

    def test_the_domain_rejects_a_malformed_key(self, client: TestClient) -> None:
        response = client.post(
            "/payments",
            json={**VALID_BODY, "pix_key": "not-an-email"},
            headers={"Idempotency-Key": "idem-001"},
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "InvalidPixKeyError"

    def test_the_error_names_a_machine_readable_code(self, client: TestClient) -> None:
        response = client.post(
            "/payments",
            json={**VALID_BODY, "pix_key_type": "CARRIER_PIGEON"},
            headers={"Idempotency-Key": "idem-001"},
        )

        detail = response.json()["detail"]
        assert detail["code"] == "InvalidPixKeyError"
        assert "supported" in detail["message"]


class TestInfrastructureFailure:
    def test_a_repository_outage_returns_503_not_422(self, events: RecordingEventPublisher) -> None:
        app = create_app(
            payments=FailingPaymentRepository(),
            clock=FixedClock(),
            id_generator=SequentialIdGenerator(ID_ONE),
            event_publisher=events,
        )

        with TestClient(app) as client:
            response = client.post(
                "/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-001"}
            )

        # Nothing was wrong with the request, so blaming the caller with a 4xx
        # would send them off to fix input that is already correct.
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "DependencyUnavailable"

    def test_the_outage_response_leaks_no_internal_detail(
        self, events: RecordingEventPublisher
    ) -> None:
        app = create_app(
            payments=FailingPaymentRepository(),
            clock=FixedClock(),
            id_generator=SequentialIdGenerator(ID_ONE),
            event_publisher=events,
        )

        with TestClient(app) as client:
            response = client.post(
                "/payments", json=VALID_BODY, headers={"Idempotency-Key": "idem-001"}
            )

        message = response.json()["detail"]["message"]
        assert "storage unreachable" not in message
        assert "Traceback" not in response.text


class TestOpenApi:
    def test_the_schema_is_generated(self, client: TestClient) -> None:
        response = client.get("/openapi.json")

        assert response.status_code == 200
        assert "/payments" in response.json()["paths"]

    def test_the_documentation_states_it_is_educational(self, client: TestClient) -> None:
        # The API description is the first thing a reader of the generated docs
        # sees. It must not be possible to mistake this for a payment system.
        description = client.get("/openapi.json").json()["info"]["description"]

        assert "Educational only" in description
