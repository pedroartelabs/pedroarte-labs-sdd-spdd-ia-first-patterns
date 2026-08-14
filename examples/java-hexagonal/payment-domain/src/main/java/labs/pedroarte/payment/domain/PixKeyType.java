package labs.pedroarte.payment.domain;

import java.util.Arrays;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public enum PixKeyType {
    EMAIL(Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")),
    PHONE(Pattern.compile("^\\+\\d{10,15}$")),
    TAX_ID(Pattern.compile("^\\d{11}(\\d{3})?$")),
    RANDOM(Pattern.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            Pattern.CASE_INSENSITIVE));

    private final Pattern pattern;

    PixKeyType(Pattern pattern) {
        this.pattern = pattern;
    }

    public boolean matches(String value) {
        return pattern.matcher(value).matches();
    }

    public static PixKeyType parse(String value) {
        try {
            return valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new InvalidPixKeyError(
                    "unknown PIX key type: " + value
                            + ". Supported: " + Arrays.stream(values())
                            .map(Enum::name)
                            .collect(Collectors.joining(", ")));
        }
    }
}
