package labs.pedroarte.payment.domain;

import java.util.Objects;
import java.util.regex.Pattern;

public record PaymentId(String value) {

    private static final Pattern UUID_SHAPE = Pattern.compile(
            "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            Pattern.CASE_INSENSITIVE);

    public PaymentId {
        Objects.requireNonNull(value, "payment id must not be null");
        if (!UUID_SHAPE.matcher(value).matches()) {
            throw new IllegalArgumentException("payment id must be UUID-shaped, got: " + value);
        }
    }
}
