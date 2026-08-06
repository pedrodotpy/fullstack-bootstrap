.PHONY: build test

COMPOSE ?= docker compose

build:
	$(COMPOSE) build

test:
	$(COMPOSE) run --rm test
