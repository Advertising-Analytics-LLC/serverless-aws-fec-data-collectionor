SHELL := /bin/bash
CFN_STACK_NAME=fec-datasync-resources
GIT_HASH_SHORT=$(shell git rev-parse --short HEAD)

all: help

##########################################
# general
##########################################

clean:
	@echo deleting all your compiled python files
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

help:
	@echo 'pick a target to run. see Makefile:'
	cat Makefile


##########################################
# docs
##########################################

.phony: serve
serve:
	@echo serving docs to http://127.0.0.1:8000
	mkdocs serve

.phony: deploy-docs
deploy-docs:
	mkdocs gh-deploy
