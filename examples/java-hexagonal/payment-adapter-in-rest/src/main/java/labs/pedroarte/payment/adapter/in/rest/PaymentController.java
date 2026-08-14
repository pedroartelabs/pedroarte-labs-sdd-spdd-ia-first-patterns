package labs.pedroarte.payment.adapter.in.rest;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import labs.pedroarte.payment.application.port.in.CreatePixPaymentCommand;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentResult;
import labs.pedroarte.payment.application.port.in.CreatePixPaymentUseCase;
import labs.pedroarte.payment.domain.DomainError;

@RestController
@RequestMapping("/payments")
public class PaymentController {

    private final CreatePixPaymentUseCase createPayment;

    public PaymentController(CreatePixPaymentUseCase createPayment) {
        this.createPayment = createPayment;
    }

    @PostMapping
    public ResponseEntity<?> create(
            @RequestBody CreatePaymentRequest request,
            @RequestHeader("Idempotency-Key") String idempotencyKey) {
        try {
            var command = new CreatePixPaymentCommand(
                    request.amount(),
                    request.currency(),
                    request.pixKey(),
                    request.pixKeyType(),
                    idempotencyKey,
                    request.description());

            CreatePixPaymentResult result = createPayment.execute(command);

            var response = new CreatePaymentResponse(
                    result.paymentId(),
                    result.status().name(),
                    result.amount(),
                    result.currency(),
                    result.createdAt());

            var status = result.alreadyExisted() ? HttpStatus.OK : HttpStatus.CREATED;
            return ResponseEntity.status(status).body(response);

        } catch (DomainError e) {
            return ResponseEntity.unprocessableEntity()
                    .body(Map.of(
                            "code", e.getClass().getSimpleName(),
                            "message", e.getMessage()));
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "service temporarily unavailable"));
        }
    }
}
