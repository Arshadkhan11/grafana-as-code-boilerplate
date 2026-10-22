PYTHON ?= python3
SERVICE ?= examples/payments-api

.PHONY: render validate test clean

render:
	$(PYTHON) scripts/render.py --config $(SERVICE)/service.yaml --out $(SERVICE)/generated

validate:
	$(PYTHON) scripts/validate.py --dir $(SERVICE)/generated

test: render
	$(PYTHON) scripts/validate.py --dir $(SERVICE)/generated
	diff -u $(SERVICE)/expected/dashboard.json $(SERVICE)/generated/dashboard.json
	diff -u $(SERVICE)/expected/alerts.json $(SERVICE)/generated/alerts.json
	@echo "OK: generated JSON matches expected/"

clean:
	rm -rf $(SERVICE)/generated
