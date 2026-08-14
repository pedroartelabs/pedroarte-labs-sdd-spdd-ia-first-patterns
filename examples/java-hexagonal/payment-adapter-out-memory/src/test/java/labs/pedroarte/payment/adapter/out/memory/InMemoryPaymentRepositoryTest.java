package labs.pedroarte.payment.adapter.out.memory;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import labs.pedroarte.payment.domain.Money;
import labs.pedroarte.payment.domain.Payment;
import labs.pedroarte.payment.domain.PaymentId;
import labs.pedroarte.payment.domain.PaymentStatus;
import labs.pedroarte.payment.domain.PixKey;

class InMemoryPaymentRepositoryTest {

    private static final PaymentId ID = new PaymentId("11111111-1111-4111-8111-111111111111");
    private static final Instant NOW = Instant.parse("2026-01-15T10:00:00Z");

    private InMemoryPaymentRepository repository;

    @BeforeEach
    void setUp() {
        repository = new InMemoryPaymentRepository();
    }

    private Payment aPayment() {
        return aPayment("idem-001");
    }

    private Payment aPayment(String idempotencyKey) {
        return Payment.create(
                ID,
                Money.of("10.50", "BRL"),
                PixKey.parse("alice@example.com", "EMAIL"),
                idempotencyKey,
                null,
                NOW);
    }

    @Test
    void savedPaymentCanBeFoundById() {
        var payment = aPayment();
        repository.save(payment);

        var found = repository.findById(ID);
        assertThat(found).isPresent();
        assertThat(found.get().id()).isEqualTo(ID);
    }

    @Test
    void unknownIdReturnsEmpty() {
        var other = new PaymentId("22222222-2222-4222-8222-222222222222");
        assertThat(repository.findById(other)).isEmpty();
    }

    @Test
    void findByIdempotencyKey() {
        repository.save(aPayment("idem-xyz"));

        var found = repository.findByIdempotencyKey("idem-xyz");
        assertThat(found).isPresent();
        assertThat(found.get().id()).isEqualTo(ID);
    }

    @Test
    void unknownIdempotencyKeyReturnsEmpty() {
        assertThat(repository.findByIdempotencyKey("never-used")).isEmpty();
    }

    @Test
    void saveTwiceUpdatesRatherThanDuplicating() {
        var payment = aPayment();
        repository.save(payment);
        payment.confirm();
        repository.save(payment);

        var found = repository.findById(ID);
        assertThat(found).isPresent();
        assertThat(found.get().status()).isEqualTo(PaymentStatus.CONFIRMED);
    }
}
