.PHONY: clean
clean:
	rm -r build dist vedro_replay.egg-info

.PHONY: install
install:
	pip3 install --quiet -r requirements.txt -r requirements-dev.txt

.PHONY: install-vedro-replay
install-vedro-replay:
	python3 setup.py install

.PHONY: test
test:
	cd tests/e2e && vedro run -vvv

.PHONY: check-types
check-types:
	python3 -m mypy vedro_replay --strict

.PHONY: check-imports
check-imports:
	python3 -m isort --check-only .

.PHONY: sort-imports
sort-imports:
	python3 -m isort .

.PHONY: check-style
check-style:
	python3 -m flake8 .

.PHONY: lint
lint: check-types check-style check-imports