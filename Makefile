SHELL := /bin/bash

all: help

clean:
	@echo deleting all your compiled python files
	bin/clean.sh

.phony: deploy
deploy:
	bin/deploy.sh

.phony: help
help:
	@echo 'pick a target to run. see Makefile:'
	cat Makefile

.phony: run
run:
	bin/run.sh

.phony: setup
setup:
	@echo make sure you've installed python3 and npm as explained in the README
	bin/dev-setup.sh

.phony: start
start:
	bin/deploy.sh
	bin/run.sh

.phony: test
test:
	bin/test.sh
