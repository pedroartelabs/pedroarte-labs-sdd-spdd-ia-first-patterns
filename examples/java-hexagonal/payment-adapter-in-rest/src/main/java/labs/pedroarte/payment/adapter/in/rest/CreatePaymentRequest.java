package labs.pedroarte.payment.adapter.in.rest;

public record CreatePaymentRequest(
        String amount,
        String currency,
        String pixKey,
        String pixKeyType,
        String description) {
}
