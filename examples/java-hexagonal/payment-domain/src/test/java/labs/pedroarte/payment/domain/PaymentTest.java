package labs.pedroarte.payment.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;

import org.junit.jupiter.api.Test;

class PaymentTest {

    private static final PaymentId ID = new PaymentId("11111111-1111-4111-8111-111111111111");
    private static final Money AMOUNT = Money.of("10.50", "BRL");
    private static final PixKey KEY = PixKey.parse("alice@example.com", "EMAIL");
    private static final Instant NOW = Instant.parse("2026-01-15T10:00:00Z");

    private Payment createPayment() {
        return Payment.create(ID, AMOUNT, KEY, "idem-001", null, NOW);
    }

    @Test
    void createsWithPendingStatus() {
        var payment = createPayment();
        assertThat(payment.status()).isEqualTo(PaymentStatus.PENDING);
    }

    @Test
    void recordsPaymentCreatedWithMaskedKey() {
        var payment = createPayment();
        var events = payment.pullEvents();

        assertThat(events).hasSize(1);
        assertThat(events.get(0)).isInstanceOf(PaymentCreated.class);

        var event = (PaymentCreated) events.get(0);
        assertThat(event.paymentId()).isEqualTo(ID.value());
        assertThat(event.maskedPixKey()).doesNotContain("alice");
    }

    @Test
    void pullEventsDrainsTheList() {
        var payment = createPayment();
        payment.pullEvents();
        assertThat(payment.pullEvents()).isEmpty();
    }

    @Test
    void confirmTransition() {
        var payment = createPayment();
        payment.confirm();
        assertThat(payment.status()).isEqualTo(PaymentStatus.CONFIRMED);
    }

    @Test
    void cancelTransition() {
        var payment = createPayment();
        payment.cancel();
        assertThat(payment.status()).isEqualTo(PaymentStatus.CANCELLED);
    }

    @Test
    void failTransition() {
        var payment = createPayment();
        payment.fail("insufficient funds");
        assertThat(payment.status()).isEqualTo(PaymentStatus.FAILED);
        assertThat(payment.failureReason()).isEqualTo("insufficient funds");
    }

    @Test
    void cannotConfirmTerminalPayment() {
        var payment = createPayment();
        payment.confirm();

        assertThatThrownBy(payment::cancel)
                .isInstanceOf(InvalidPaymentTransitionError.class)
                .hasMessageContaining("cannot cancel");
    }

    @Test
    void identityBasedEquality() {
        var a = Payment.create(ID, AMOUNT, KEY, "idem-a", null, NOW);
        var b = Payment.create(ID, Money.of("99.99", "USD"), KEY, "idem-b", null, NOW);
        assertThat(a).isEqualTo(b);
    }

    @Test
    void rejectsBlankIdempotencyKey() {
        assertThatThrownBy(() -> Payment.create(ID, AMOUNT, KEY, "", null, NOW))
                .isInstanceOf(IllegalArgumentException.class);
    }
}
