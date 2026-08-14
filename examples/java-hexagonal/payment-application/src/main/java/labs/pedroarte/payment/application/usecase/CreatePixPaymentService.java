package labs.pedroarte.payment.application.usecase;

import labs.pedroarte.payment.application.port.in.CreatePixPaymentCommand;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentResult;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentUseCase;
import labs.pedroarte.payment.application.port.out.Clock;
import labs.pedroarte.payment.application.port.out.IdGenerator;
import labs.pedroarte.payment.application.port.out.PaymentEventPublisher;
import labs.pedroarte.payment.application.port.out.PaymentRepository;
import labs.pedroarte.payment.domain.Money;
import labs.pedroarte.payment.domain.Payment;
import labs.pedroarte.payment.domain.PaymentId;
import labs.pedroarte.payment.domain.PixKey;

public final class CreatePixPaymentService implements CreatePixPaymentUseCase {

    private final PaymentRepository payments;
    private final IdGenerator idGenerator;
    private final Clock clock;
    private final PaymentEventPublisher eventPublisher;

    public CreatePixPaymentService(PaymentRepository payments,
                                    IdGenerator idGenerator,
                                    Clock clock,
                                    PaymentEventPublisher eventPublisher) {
        this.payments = payments;
        this.idGenerator = idGenerator;
        this.clock = clock;
        this.eventPublisher = eventPublisher;
    }

    @Override
    public CreatePixPaymentResult execute(CreatePixPaymentCommand command) {
        var existing = payments.findByIdempotencyKey(command.idempotencyKey());
        if (existing.isPresent()) {
            return toResult(existing.get(), true);
        }

        var money = Money.of(command.amount(), command.currency());
        var pixKey = PixKey.parse(command.pixKey(), command.pixKeyType());
        var id = new PaymentId(idGenerator.next());

        var payment = Payment.create(
                id, money, pixKey,
                command.idempotencyKey(),
                command.description(),
                clock.now());

        payments.save(payment);

        for (var event : payment.pullEvents()) {
            eventPublisher.publish(event);
        }

        return toResult(payment, false);
    }

    private static CreatePixPaymentResult toResult(Payment payment, boolean alreadyExisted) {
        return new CreatePixPaymentResult(
                payment.id().value(),
                payment.status(),
                payment.amount().amount().toPlainString(),
                payment.amount().currency(),
                payment.createdAt(),
                alreadyExisted);
    }
}
