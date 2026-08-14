package labs.pedroarte.payment.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;

class MoneyTest {

    @Test
    void createsValidMoney() {
        var money = Money.of("10.50", "BRL");

        assertThat(money.amount().toPlainString()).isEqualTo("10.50");
        assertThat(money.currency()).isEqualTo("BRL");
    }

    @Test
    void normaliseCurrencyToUpperCase() {
        var money = Money.of("1.00", "brl");

        assertThat(money.currency()).isEqualTo("BRL");
    }

    @Test
    void rejectsNonPositiveAmount() {
        assertThatThrownBy(() -> Money.of("0", "BRL"))
                .isInstanceOf(InvalidMoneyError.class)
                .hasMessageContaining("must be positive");
    }

    @Test
    void rejectsNegativeAmount() {
        assertThatThrownBy(() -> Money.of("-1.00", "BRL"))
                .isInstanceOf(InvalidMoneyError.class)
                .hasMessageContaining("must be positive");
    }

    @Test
    void rejectsSubCentPrecision() {
        assertThatThrownBy(() -> Money.of("1.001", "BRL"))
                .isInstanceOf(InvalidMoneyError.class)
                .hasMessageContaining("decimal places");
    }

    @Test
    void rejectsUnsupportedCurrency() {
        assertThatThrownBy(() -> Money.of("1.00", "XYZ"))
                .isInstanceOf(InvalidMoneyError.class)
                .hasMessageContaining("unsupported currency");
    }

    @Test
    void twoMoneyWithSameValuesAreEqual() {
        var a = Money.of("10.50", "BRL");
        var b = Money.of("10.50", "BRL");

        assertThat(a).isEqualTo(b);
        assertThat(a.hashCode()).isEqualTo(b.hashCode());
    }
}
