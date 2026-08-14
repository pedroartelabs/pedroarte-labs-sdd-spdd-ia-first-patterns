package labs.pedroarte.payment.application.usecase;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import labs.pedroarte.payment.adapter.out.memory.InMemoryPaymentRepository;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentCommand;
import labs.pedroarte.payment.application.port.out.Clock;
import labs.pedroarte.payment.application.port.out.IdGenerator;
import labs.pedroarte.payment.application.port.out.PaymentEventPublisher;
import labs.pedroarte.payment.domain.InvalidMoneyError;
import labs.pedroarte.payment.domain.InvalidPixKeyError;
import labs.pedroarte.payment.domain.PaymentStatus;

class CreatePixPaymentServiceTest {

    private static final String ID_ONE = "11111111-1111-4111-8111-111111111111";
    private static final String ID_TWO = "22222222-2222-4222-8222-222222222222";
    private static final Instant FIXED_INSTANT = Instant.parse("2026-01-15T10:00:00Z");

    private InMemoryPaymentRepository repository;
    private List<Object> publishedEvents;
    private CreatePixPaymentService service;

    @BeforeEach
    void setUp() {
        repository = new InMemoryPaymentRepository();
        publishedEvents = new ArrayList<>();
        var ids = new AtomicInteger(0);
        String[] idPool = {ID_ONE, ID_TWO};

        IdGenerator idGenerator = () -> idPool[ids.getAndIncrement()];
        Clock clock = () -> FIXED_INSTANT;
        PaymentEventPublisher publisher = publishedEvents::add;

        service = new CreatePixPaymentService(repository, idGenerator, clock, publisher);
    }

    private CreatePixPaymentCommand command() {
        return command("idem-001");
    }

    private CreatePixPaymentCommand command(String idempotencyKey) {
        return new CreatePixPaymentCommand(
                "10.50", "BRL", "alice@example.com", "EMAIL", idempotencyKey, null);
    }

    @Test
    void createsAPendingPayment() {
        var result = service.execute(command());

        assertThat(result.paymentId()).isEqualTo(ID_ONE);
        assertThat(result.status()).isEqualTo(PaymentStatus.PENDING);
        assertThat(result.alreadyExisted()).isFalse();
    }

    @Test
    void usesTheInjectedClockAndIdGenerator() {
        var result = service.execute(command());

        assertThat(result.paymentId()).isEqualTo(ID_ONE);
        assertThat(result.createdAt()).isEqualTo(FIXED_INSTANT);
    }

    @Test
    void publishesTheCreationEvent() {
        service.execute(command());
        assertThat(publishedEvents).hasSize(1);
    }

    @Test
    void replayReturnsTheOriginalPayment() {
        var first = service.execute(command("idem-retry"));
        var second = service.execute(command("idem-retry"));

        assertThat(second.paymentId()).isEqualTo(first.paymentId());
        assertThat(second.alreadyExisted()).isTrue();
    }

    @Test
    void replayPublishesNothing() {
        service.execute(command("idem-retry"));
        publishedEvents.clear();
        service.execute(command("idem-retry"));

        assertThat(publishedEvents).isEmpty();
    }

    @Test
    void distinctKeysCreateDistinctPayments() {
        var first = service.execute(command("idem-1"));
        var second = service.execute(command("idem-2"));

        assertThat(first.paymentId()).isEqualTo(ID_ONE);
        assertThat(second.paymentId()).isEqualTo(ID_TWO);
    }

    @Test
    void rejectsNonPositiveAmount() {
        var cmd = new CreatePixPaymentCommand("0", "BRL", "alice@example.com", "EMAIL", "idem-001", null);
        assertThatThrownBy(() -> service.execute(cmd))
                .isInstanceOf(InvalidMoneyError.class);
    }

    @Test
    void rejectsMalformedKey() {
        var cmd = new CreatePixPaymentCommand("10.50", "BRL", "not-an-email", "EMAIL", "idem-001", null);
        assertThatThrownBy(() -> service.execute(cmd))
                .isInstanceOf(InvalidPixKeyError.class);
    }
}
