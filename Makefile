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
# cloudformation
##########################################

deploy-cfn:
	aws cloudformation deploy \
	    --no-fail-on-empty-changeset \
	    --stack-name "$(CFN_STACK_NAME)" \
	    --template-file cloudformation/prerequisite-cloudformation-resources.yml

create-change-set:
	$(eval cs_name := change-set-$(GIT_HASH_SHORT))
	aws cloudformation create-change-set \
		--change-set-name $(cs_name) \
	    --stack-name "$(CFN_STACK_NAME)" \
		--template-body file://cloudformation/prerequisite-cloudformation-resources.yml \
	> $(cs_name).json

diff-cfn: create-change-set
	$(eval cs_name := change-set-$(GIT_HASH_SHORT))
	$(eval cs_id := $(shell cat $(cs_name).json | jq '.Id'))
	rm $(cs_name).json

	aws cloudformation wait change-set-create-complete \
		--change-set-name $(cs_id)

	aws cloudformation describe-change-set \
		--change-set-name $(cs_id) \
		--output yaml

apply-cfn: diff-cfn
	aws cloudformation execute-change-set \
		--change-set-name $(cs_id) \
		--output yaml


##########################################
# serverless
##########################################

diff-sls:
	sls package && sls diff

.phony: deploy-sls
deploy-sls:
	serverless deploy


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
