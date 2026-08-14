package labs.pedroarte.payment.domain;

public final class InvalidPaymentTransitionError extends DomainError {
    public InvalidPaymentTransitionError(String message) {
        super(message);
    }
}
