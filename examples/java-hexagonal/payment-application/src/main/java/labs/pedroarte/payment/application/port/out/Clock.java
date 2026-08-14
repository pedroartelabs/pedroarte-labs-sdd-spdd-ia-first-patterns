package labs.pedroarte.payment.application.port.out;

import java.time.Instant;

public interface Clock {
    Instant now();
}
