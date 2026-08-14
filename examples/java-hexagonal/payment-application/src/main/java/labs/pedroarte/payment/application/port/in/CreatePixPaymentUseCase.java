package labs.pedroarte.payment.application.port.in;

public interface CreatePixPaymentUseCase {
    CreatePixPaymentResult execute(CreatePixPaymentCommand command);
}
