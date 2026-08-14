package labs.pedroarte.payment.domain;

public enum PaymentStatus {
    PENDING,
    CONFIRMED,
    CANCELLED,
    FAILED;

    public boolean isTerminal() {
        return this == CONFIRMED || this == CANCELLED || this == FAILED;
    }
}
