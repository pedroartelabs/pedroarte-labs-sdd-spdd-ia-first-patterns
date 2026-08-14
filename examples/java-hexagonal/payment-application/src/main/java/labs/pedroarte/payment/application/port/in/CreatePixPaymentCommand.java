package labs.pedroarte.payment.application.port.in;

public record CreatePixPaymentCommand(
        String amount,
        String currency,
        String pixKey,
        String pixKeyType,
        String idempotencyKey,
        String description) {
}
