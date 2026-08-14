package labs.pedroarte.payment.application.port.out;

import java.util.Optional;

import labs.pedroarte.payment.domain.Payment;
import labs.pedroarte.payment.domain.PaymentId;

public interface PaymentRepository {
    void save(Payment payment);
    Optional<Payment> findById(PaymentId id);
    Optional<Payment> findByIdempotencyKey(String idempotencyKey);
}
