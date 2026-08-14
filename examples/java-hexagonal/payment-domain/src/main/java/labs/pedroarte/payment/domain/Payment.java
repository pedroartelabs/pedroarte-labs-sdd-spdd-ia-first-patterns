package labs.pedroarte.payment.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

public final class Payment {

    private final PaymentId id;
    private final Money amount;
    private final PixKey pixKey;
    private final String idempotencyKey;
    private final String description;
    private final Instant createdAt;
    private PaymentStatus status;
    private String failureReason;
    private final List<Object> events = new ArrayList<>();

    private Payment(PaymentId id, Money amount, PixKey pixKey,
                    String idempotencyKey, String description, Instant createdAt) {
        this.id = id;
        this.amount = amount;
        this.pixKey = pixKey;
        this.idempotencyKey = idempotencyKey;
        this.description = description;
        this.createdAt = createdAt;
        this.status = PaymentStatus.PENDING;
    }

    public static Payment create(PaymentId id, Money amount, PixKey pixKey,
                                  String idempotencyKey, String description,
                                  Instant createdAt) {
        Objects.requireNonNull(id);
        Objects.requireNonNull(amount);
        Objects.requireNonNull(pixKey);
        Objects.requireNonNull(idempotencyKey);
        Objects.requireNonNull(createdAt);

        if (idempotencyKey.isBlank()) {
            throw new IllegalArgumentException("idempotency key must not be blank");
        }
        if (idempotencyKey.length() > 64) {
            throw new IllegalArgumentException("idempotency key must be at most 64 characters");
        }
        if (description != null && description.length() > 140) {
            throw new IllegalArgumentException("description must be at most 140 characters");
        }

        var payment = new Payment(id, amount, pixKey, idempotencyKey, description, createdAt);

        payment.events.add(new PaymentCreated(
                id.value(),
                amount.amount().toPlainString(),
                amount.currency(),
                pixKey.masked(),
                pixKey.type().name(),
                createdAt));

        return payment;
    }

    public void confirm() {
        requireNonTerminal("confirm");
        this.status = PaymentStatus.CONFIRMED;
    }

    public void cancel() {
        requireNonTerminal("cancel");
        this.status = PaymentStatus.CANCELLED;
    }

    public void fail(String reason) {
        requireNonTerminal("fail");
        Objects.requireNonNull(reason, "failure reason must not be null");
        this.status = PaymentStatus.FAILED;
        this.failureReason = reason;
    }

    private void requireNonTerminal(String action) {
        if (status.isTerminal()) {
            throw new InvalidPaymentTransitionError(
                    "cannot %s a payment in %s status".formatted(action, status));
        }
    }

    public List<Object> pullEvents() {
        var snapshot = List.copyOf(events);
        events.clear();
        return snapshot;
    }

    // --- Accessors ---

    public PaymentId id() { return id; }
    public Money amount() { return amount; }
    public PixKey pixKey() { return pixKey; }
    public String idempotencyKey() { return idempotencyKey; }
    public String description() { return description; }
    public Instant createdAt() { return createdAt; }
    public PaymentStatus status() { return status; }
    public String failureReason() { return failureReason; }

    @Override
    public boolean equals(Object o) {
        return o instanceof Payment p && id.equals(p.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
