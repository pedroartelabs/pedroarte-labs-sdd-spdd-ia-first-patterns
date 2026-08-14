package labs.pedroarte.payment.domain;

import java.time.Instant;

public record PaymentCreated(
        String paymentId,
        String amount,
        String currency,
        String maskedPixKey,
        String pixKeyType,
        Instant createdAt) {
}
