
REQUIRED_BUILD_BINS := poetry poe

# Check https://python-poetry.org/docs/#installation for other installations methods for poetry.
.PHONY: init
init:
	curl -sSL https://install.python-poetry.org | python3 -
	pip install poethepoet
	poetry self add poetry-plugin-sort

.PHONY: install
install:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe install

.PHONY: uninstall
uninstall:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe uninstall

.PHONY: install/dev
install/dev:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe dev

.PHONY: lint
lint:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe lint

.PHONY: lint/check
lint/check:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe check

.PHONY: lock
lock:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe lock

.PHONY: test
test/nodocker:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe test --ignore=tests/src/guardx/test_guardx.py

.PHONY: test
test:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe test

.PHONY: clean
clean:
	$(foreach bin,$(REQUIRED_BUILD_BINS), $(if $(shell command -v $(bin) 2> /dev/null),,$(error Couldn't find `$(bin)`. Please run `make init`)))
	poe clean

.PHONY:
containers/podman:
	podman build -t lab-validator -f src/guardx/containers/Dockerfile.sandbox
	podman build -t lab-analyzer -f src/guardx/containers/Dockerfile.analysis

.PHONY:
containers/docker:
	docker buildx build -t lab-validator -f src/guardx/containers/Dockerfile.sandbox .
	docker buildx build -t lab-analyzer -f src/guardx/containers/Dockerfile.analysis .

.PHONY: help
help:
	@echo "This Makefile is offered for convenience. For regular development, you can use 'poe' directly."
	@echo "To install Poetry and poe, run 'make init'."
	@echo "For help with poe, run 'poe -h'."
	@echo ""
	@echo "The following are the valid targets for this Makefile:"
	@echo "...install           Install package from sources"
	@echo "...install/dev       Install source and packages for linting, testing and development"
	@echo "...uninstall         Uninstall package"
	@echo "...lock              Lock dependencies"
	@echo "...lint              Check and fix lint errors"
	@echo "...lint/check        Check for lint errors"
	@echo "...test              Run all tests"
	@echo "...containers/podman Build container images using podman"
	@echo "...containers/docker Build container images using docker"
	@echo "...clean             Remove all artifacts and builds"


