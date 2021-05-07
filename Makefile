SHELL := /bin/bash

all: help

clean:
	@echo deleting all your compiled python files
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.phony: deploy
deploy:
	bin/deploy.sh

.phony: deploy-docs
deploy-docs:
	mkdocs gh-deploy

.phony: help
help:
	@echo 'pick a target to run. see Makefile:'
	cat Makefile

.phony: run
run:
	bin/run.sh

.phony: serve
serve:
	@echo serving docs to http://127.0.0.1:8000
	mkdocs serve

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
