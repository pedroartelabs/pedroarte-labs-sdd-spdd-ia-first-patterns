package labs.pedroarte.payment.domain;

public final class InvalidPixKeyError extends DomainError {
    public InvalidPixKeyError(String message) {
        super(message);
    }
}
