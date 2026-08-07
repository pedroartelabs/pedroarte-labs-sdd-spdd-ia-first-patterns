"""REST inbound adapter.

Its entire job: validate the shape of the request, turn it into a command, call
the inbound port, and translate the outcome back into HTTP. There is no business
rule here, and there must never be one — a rule that lives in a controller
cannot be reached by the CLI, the consumer or the scheduler (ARCH-010).

The router is built by a factory that receives the use case. Nothing is
imported from the composition root, so this module has no idea which repository
implementation is in play (ARCH-007).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from payment.adapters.inbound.rest.dto import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    ErrorResponse,
)
from payment.application.errors import OutboundPortError
from payment.application.ports.inbound.create_pix_payment import CreatePixPaymentUseCase
from payment.domain.errors import DomainError

_IDEMPOTENCY_HEADER = "Idempotency-Key"

# Written as a literal rather than `status.HTTP_422_...`: Starlette renamed the
# constant from UNPROCESSABLE_ENTITY to UNPROCESSABLE_CONTENT, so referencing
# either name couples this adapter to a specific Starlette version. The number
# is what actually goes on the wire and it is not going to change.
_HTTP_UNPROCESSABLE_CONTENT = 422


def create_payment_router(use_case: CreatePixPaymentUseCase) -> APIRouter:
    """Build the payments router around a use case.

    A factory rather than a module-level router with a global dependency: the
    wiring stays in bootstrap, and a test can build a router over fakes without
    patching anything.
    """
    router = APIRouter(prefix="/payments", tags=["payments"])

    @router.post(
        "",
        status_code=status.HTTP_201_CREATED,
        response_model=CreatePaymentResponse,
        responses={
            200: {"description": "Idempotent replay of an existing payment"},
            _HTTP_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "The request violates a business rule",
            },
            503: {"model": ErrorResponse, "description": "A downstream dependency failed"},
        },
        summary="Create a PIX payment",
    )
    def create_payment(
        request: CreatePaymentRequest,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias=_IDEMPOTENCY_HEADER,
                min_length=1,
                max_length=64,
                description="Repeat this key to retry safely; the same payment is returned.",
            ),
        ],
    ) -> CreatePaymentResponse:
        try:
            result = use_case.execute(request.to_command(idempotency_key))
        except DomainError as exc:
            # A business rule was violated: the caller can fix this, so it is a
            # 422 and the domain's own message is the most useful thing to say.
            raise HTTPException(
                status_code=_HTTP_UNPROCESSABLE_CONTENT,
                detail=ErrorResponse(code=type(exc).__name__, message=str(exc)).model_dump(),
            ) from exc
        except OutboundPortError as exc:
            # Infrastructure failed. Nothing about the request was wrong, so we
            # do not blame the caller — and we do not leak the underlying
            # driver message, which may name hosts or credentials (SEC-004).
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    code="DependencyUnavailable",
                    message=f"{exc.port} is temporarily unavailable",
                ).model_dump(),
            ) from exc

        if result.already_existed:
            # The retry created nothing, so 201 would be a lie. 200 tells an
            # honest client that this was a replay.
            response.status_code = status.HTTP_200_OK

        return CreatePaymentResponse.from_result(result)

    return router
