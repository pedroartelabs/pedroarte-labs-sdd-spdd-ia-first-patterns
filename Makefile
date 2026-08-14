.PHONY: help doctor setup generate-agent-rules check-rule-drift \
       validate-specs validate-prompts validate-traceability \
       verify-architecture verify-python verify-java verify-security verify-docs \
       verify spec-new

PYTHON := python
PY_HEX := examples/python-hexagonal
JAVA_HEX := examples/java-hexagonal

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-28s\033[0m %s\n", $$1, $$2}'

doctor: ## Verify the local toolchain
	$(PYTHON) scripts/doctor.py

setup: ## Install dev dependencies
	cd $(PY_HEX) && pip install -e ".[dev]"

generate-agent-rules: ## Regenerate agent instruction files from policy
	$(PYTHON) scripts/generate-agent-rules.py

check-rule-drift: ## Fail if generated files drifted from policy
	$(PYTHON) scripts/check-generated-rule-drift.py

validate-specs: ## SDD lifecycle and schema validation
	$(PYTHON) scripts/validate-specs.py

validate-prompts: ## SPDD REASONS validation
	$(PYTHON) scripts/validate-prompts.py

validate-traceability: ## Requirement -> code -> test -> evidence
	$(PYTHON) scripts/validate-traceability.py

verify-architecture: ## ArchUnit + Import Linter + negative fixtures
	cd $(PY_HEX) && $(PYTHON) -m pytest tests/architecture/ -v

verify-python: ## Run all Python checks
	cd $(PY_HEX) && $(PYTHON) -m pytest tests/ -v --tb=short
	cd $(PY_HEX) && $(PYTHON) -m mypy src/ tests/ --strict
	cd $(PY_HEX) && $(PYTHON) -m ruff check src/ tests/
	cd $(PY_HEX) && $(PYTHON) -m ruff format --check src/ tests/
	cd $(PY_HEX) && $(PYTHON) -m bandit -r src/ -c pyproject.toml

verify-java: ## Run all Java checks (requires JDK)
	cd $(JAVA_HEX) && ./mvnw verify

verify-security: ## Run security scans
	cd $(PY_HEX) && $(PYTHON) -m bandit -r src/ -c pyproject.toml

verify-docs: ## Validate documentation completeness
	@echo "Documentation validation not yet implemented"

verify: check-rule-drift verify-python verify-architecture ## Everything before a pull request
	@echo "All verifications passed."

spec-new: ## Create a new spec directory (NAME="..." TYPE=feature)
	$(PYTHON) scripts/create-spec.py --name "$(NAME)" --type "$(TYPE)"
