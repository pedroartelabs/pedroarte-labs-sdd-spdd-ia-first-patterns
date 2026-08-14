package labs.pedroarte.payment.application.port.out;

public interface PaymentEventPublisher {
    void publish(Object event);
}
