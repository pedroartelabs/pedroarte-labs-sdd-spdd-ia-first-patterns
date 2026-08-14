package labs.pedroarte.payment.bootstrap;

import java.time.Instant;
import java.util.UUID;
import java.util.logging.Logger;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import labs.pedroarte.payment.adapter.out.memory.InMemoryPaymentRepository;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentUseCase;
import labs.pedroarte.payment.application.port.out.Clock;
import labs.pedroarte.payment.application.port.out.IdGenerator;
import labs.pedroarte.payment.application.port.out.PaymentEventPublisher;
import labs.pedroarte.payment.application.port.out.PaymentRepository;
import labs.pedroarte.payment.application.usecase.CreatePixPaymentService;

@Configuration
public class PaymentConfiguration {

    private static final Logger LOG = Logger.getLogger(PaymentConfiguration.class.getName());

    @Bean
    public PaymentRepository paymentRepository() {
        return new InMemoryPaymentRepository();
    }

    @Bean
    public Clock clock() {
        return Instant::now;
    }

    @Bean
    public IdGenerator idGenerator() {
        return () -> UUID.randomUUID().toString();
    }

    @Bean
    public PaymentEventPublisher eventPublisher() {
        return event -> LOG.info("Event published: " + event.getClass().getSimpleName());
    }

    @Bean
    public CreatePixPaymentUseCase createPixPaymentUseCase(
            PaymentRepository payments,
            IdGenerator idGenerator,
            Clock clock,
            PaymentEventPublisher eventPublisher) {
        return new CreatePixPaymentService(payments, idGenerator, clock, eventPublisher);
    }
}
