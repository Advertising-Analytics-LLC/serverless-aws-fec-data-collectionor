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

.phony: run-sync
run-sync:
	sls invoke -f CommitteeSync

.phony: run-loader
run-loader:
	sls invoke -f CommitteeLoader

.phony: setup
setup:
	@echo make sure you've installed python3 and npm as explained in the README
	bin/dev-setup.sh

.phony: test
test:
	@echo 'pick a target to run. see Makefile:'
	pytest

.phony: test-sync
test-sync:
	sls invoke local -f CommitteeSync

.phony: test-loader
test-loader:
	sls invoke local -f CommitteLoader
