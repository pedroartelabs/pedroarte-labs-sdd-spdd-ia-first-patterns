package labs.pedroarte.payment.domain;

import java.math.BigDecimal;
import java.util.Objects;
import java.util.Set;

public record Money(BigDecimal amount, String currency) {

    private static final Set<String> SUPPORTED_CURRENCIES = Set.of("BRL", "USD", "EUR");
    private static final int MAX_MINOR_UNIT_DIGITS = 2;

    public Money {
        Objects.requireNonNull(amount, "amount must not be null");
        Objects.requireNonNull(currency, "currency must not be null");

        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidMoneyError("amount must be positive, got " + amount);
        }

        if (amount.scale() > MAX_MINOR_UNIT_DIGITS) {
            throw new InvalidMoneyError(
                    "amount must have at most %d decimal places, got %s".formatted(MAX_MINOR_UNIT_DIGITS, amount));
        }

        String upper = currency.toUpperCase();
        if (!SUPPORTED_CURRENCIES.contains(upper)) {
            throw new InvalidMoneyError("unsupported currency: " + currency
                    + ". Supported: " + SUPPORTED_CURRENCIES);
        }

        currency = upper;
    }

    public static Money of(String amount, String currency) {
        return new Money(new BigDecimal(amount), currency);
    }
}
