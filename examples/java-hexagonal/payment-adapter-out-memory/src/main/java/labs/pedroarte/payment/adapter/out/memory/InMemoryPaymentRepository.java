package labs.pedroarte.payment.adapter.out.memory;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

import labs.pedroarte.payment.application.port.out.PaymentRepository;
import labs.pedroarte.payment.domain.Payment;
import labs.pedroarte.payment.domain.PaymentId;

public final class InMemoryPaymentRepository implements PaymentRepository {

    private final Map<String, Payment> byId = new ConcurrentHashMap<>();
    private final Map<String, String> idempotencyIndex = new ConcurrentHashMap<>();

    @Override
    public void save(Payment payment) {
        byId.put(payment.id().value(), payment);
        idempotencyIndex.put(payment.idempotencyKey(), payment.id().value());
    }

    @Override
    public Optional<Payment> findById(PaymentId id) {
        return Optional.ofNullable(byId.get(id.value()));
    }

    @Override
    public Optional<Payment> findByIdempotencyKey(String idempotencyKey) {
        var paymentId = idempotencyIndex.get(idempotencyKey);
        if (paymentId == null) {
            return Optional.empty();
        }
        return findById(new PaymentId(paymentId));
    }

    public void clear() {
        byId.clear();
        idempotencyIndex.clear();
    }
}
