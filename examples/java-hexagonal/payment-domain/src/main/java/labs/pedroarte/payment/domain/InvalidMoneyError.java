package labs.pedroarte.payment.domain;

public final class InvalidMoneyError extends DomainError {
    public InvalidMoneyError(String message) {
        super(message);
    }
}
