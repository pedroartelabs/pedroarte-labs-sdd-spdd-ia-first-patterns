package labs.pedroarte.payment.domain;

public abstract sealed class DomainError extends RuntimeException
        permits InvalidMoneyError, InvalidPixKeyError, InvalidPaymentTransitionError {

    protected DomainError(String message) {
        super(message);
    }
}
