package labs.pedroarte.payment.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class PixKeyTest {

    @ParameterizedTest
    @CsvSource({
        "alice@example.com, EMAIL",
        "+5511999998888, PHONE",
        "12345678901, TAX_ID",
        "11111111-1111-4111-8111-111111111111, RANDOM"
    })
    void acceptsValidKeys(String value, String type) {
        var key = PixKey.parse(value, type);
        assertThat(key.value()).isEqualTo(value);
    }

    @Test
    void rejectsMalformedEmail() {
        assertThatThrownBy(() -> PixKey.parse("not-an-email", "EMAIL"))
                .isInstanceOf(InvalidPixKeyError.class)
                .hasMessageContaining("not a well-formed");
    }

    @Test
    void rejectsUnknownType() {
        assertThatThrownBy(() -> PixKey.parse("alice@example.com", "CARRIER_PIGEON"))
                .isInstanceOf(InvalidPixKeyError.class)
                .hasMessageContaining("unknown PIX key type")
                .hasMessageContaining("Supported");
    }

    @Test
    void masksEmail() {
        var key = PixKey.parse("alice@example.com", "EMAIL");
        assertThat(key.masked()).doesNotContain("alice");
        assertThat(key.masked()).contains("@example.com");
    }

    @Test
    void masksPhone() {
        var key = PixKey.parse("+5511999998888", "PHONE");
        assertThat(key.masked()).doesNotContain("99999");
    }

    @Test
    void rejectsBlankValue() {
        assertThatThrownBy(() -> new PixKey("", PixKeyType.EMAIL))
                .isInstanceOf(InvalidPixKeyError.class)
                .hasMessageContaining("blank");
    }
}
