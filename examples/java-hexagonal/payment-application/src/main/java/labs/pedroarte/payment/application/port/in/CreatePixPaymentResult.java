package labs.pedroarte.payment.application.port.in;

import java.time.Instant;

import labs.pedroarte.payment.domain.PaymentStatus;

public record CreatePixPaymentResult(
        String paymentId,
        PaymentStatus status,
        String amount,
        String currency,
        Instant createdAt,
        boolean alreadyExisted) {
}
