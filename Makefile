all: run

run:
	@docker compose up --force-recreate --remove-orphans

setup:
	@git submodule update --init

.PHONY: all run setup
