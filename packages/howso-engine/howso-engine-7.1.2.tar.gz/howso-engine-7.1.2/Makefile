.PHONY: check clean dev production test

# `make requirements.txt` builds the runtime requirements
requirements.txt: requirements.in
	pip-compile requirements.in

# `make requirements-dev.txt` builds the development-only requirements
requirements-dev.txt: requirements-dev.in requirements.txt
	pip-compile requirements-dev.in

# Checks that `pip-compile` exists
check:
	@which pip-compile > /dev/null

# `make clean` will clear out any requirements*.txt files, but only if `pip-compile` exists.
clean: check
	rm -f requirements.txt requirements-dev.txt

# `make dev` will compile then install development requirements.
dev:
	rm -f requirements.txt requirements-dev.txt
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt

# `make production` will install only the dependencies required for run-time or production
production:
	rm -f requirements.txt
	pip-compile requirements.in
	pip-sync requirements.txt

# Run the lint/style/complexity check
lint:
	flake8

# Run tests (with coverage)
test:
	coverage run -m pytest && coverage report -m

licenses:
	pip list --format=freeze | cut -d= -f1 | xargs pip show > LICENSE-3RD-PARTY.txt
