package labs.pedroarte.payment.adapter.in.rest;

import java.time.Instant;

public record CreatePaymentResponse(
        String paymentId,
        String status,
        String amount,
        String currency,
        Instant createdAt) {
}
