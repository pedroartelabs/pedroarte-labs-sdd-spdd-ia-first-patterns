package labs.pedroarte.payment.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

class HexagonalArchitectureTest {

    private static JavaClasses classes;

    @BeforeAll
    static void importClasses() {
        classes = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("labs.pedroarte.payment");
    }

    // ARCH-001: Domain must not depend on frameworks
    @Test
    void domainDoesNotDependOnSpring() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("org.springframework..")
                .as("ARCH-001: domain must not depend on Spring")
                .check(classes);
    }

    @Test
    void domainDoesNotDependOnJakartaPersistence() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("jakarta.persistence..")
                .as("ARCH-001: domain must not depend on JPA")
                .check(classes);
    }

    @Test
    void domainDoesNotDependOnJackson() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("com.fasterxml.jackson..")
                .as("ARCH-001: domain must not depend on Jackson")
                .check(classes);
    }

    // ARCH-002: Domain must not depend on outer layers
    @Test
    void domainDoesNotDependOnApplication() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("..application..")
                .as("ARCH-002: domain must not depend on application")
                .check(classes);
    }

    @Test
    void domainDoesNotDependOnAdapters() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("..adapter..")
                .as("ARCH-002: domain must not depend on adapters")
                .check(classes);
    }

    @Test
    void domainDoesNotDependOnBootstrap() {
        noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("..bootstrap..")
                .as("ARCH-002: domain must not depend on bootstrap")
                .check(classes);
    }

    // ARCH-003: Application must not depend on adapters
    @Test
    void applicationDoesNotDependOnAdapters() {
        noClasses()
                .that().resideInAPackage("..application..")
                .should().dependOnClassesThat().resideInAPackage("..adapter..")
                .as("ARCH-003: application must not depend on adapters")
                .check(classes);
    }

    @Test
    void applicationDoesNotDependOnBootstrap() {
        noClasses()
                .that().resideInAPackage("..application..")
                .should().dependOnClassesThat().resideInAPackage("..bootstrap..")
                .as("ARCH-003: application must not depend on bootstrap")
                .check(classes);
    }

    // ARCH-004/005: Adapters must not depend on each other
    @Test
    void inboundAdaptersDoNotDependOnOutboundAdapters() {
        noClasses()
                .that().resideInAPackage("..adapter.in..")
                .should().dependOnClassesThat().resideInAPackage("..adapter.out..")
                .as("ARCH-004: inbound adapters must not depend on outbound adapters")
                .check(classes);
    }

    @Test
    void outboundAdaptersDoNotDependOnInboundAdapters() {
        noClasses()
                .that().resideInAPackage("..adapter.out..")
                .should().dependOnClassesThat().resideInAPackage("..adapter.in..")
                .as("ARCH-005: outbound adapters must not depend on inbound adapters")
                .check(classes);
    }
}
