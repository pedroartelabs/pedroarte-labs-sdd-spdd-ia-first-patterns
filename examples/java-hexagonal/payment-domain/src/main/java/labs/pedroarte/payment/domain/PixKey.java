package labs.pedroarte.payment.domain;

import java.util.Objects;

public record PixKey(String value, PixKeyType type) {

    public PixKey {
        Objects.requireNonNull(value, "PIX key value must not be null");
        Objects.requireNonNull(type, "PIX key type must not be null");

        if (value.isBlank()) {
            throw new InvalidPixKeyError("PIX key value must not be blank");
        }

        if (!type.matches(value)) {
            throw new InvalidPixKeyError(
                    "not a well-formed %s PIX key: %s".formatted(type, mask(value, type)));
        }
    }

    public static PixKey parse(String value, String typeName) {
        PixKeyType type = PixKeyType.parse(typeName);
        return new PixKey(value, type);
    }

    public String masked() {
        return mask(value, type);
    }

    private static String mask(String value, PixKeyType type) {
        return switch (type) {
            case EMAIL -> {
                int at = value.indexOf('@');
                yield (at > 1 ? value.substring(0, 2) : value.substring(0, 1)) + "***" + value.substring(at);
            }
            case PHONE -> value.substring(0, 4) + "****" + value.substring(value.length() - 2);
            case TAX_ID -> value.substring(0, 3) + ".***.***-**";
            case RANDOM -> value.substring(0, 8) + "-****-****-****-************";
        };
    }
}
