FOLDER_NAME := $(shell pwd | xargs basename)
GIT_BRANCH=$(shell git branch --show-current)
NEW= := $(NEW)
OUTFILE_PATH=$(GIT_BRANCH)-$(TF_WORKSPACE).out
SHELL := /bin/bash
TF_WORKSPACE := $(shell terraform workspace show)
WORKSPACE ?= $(TF_WORKSPACE)
VAR_FILES := #-var-file $(WORKSPACE).tfvars


clean:
	@echo WARNING - removing local terraform dirs
	rm -rf .terraform

init:
	terraform init
	$(shell [ ! -z $(WORKSPACE) ] && terraform workspace select $(WORKSPACE);)

list: init
	@echo listing terraform workspaces:
	terraform workspace list

refresh: init
	terraform refresh $(VAR_FILES)

plan: init
	@echo planning changes to the $(TF_WORKSPACE) workspace
	terraform plan $(VAR_FILES)

fplan:
	@echo planning changes to the $(TF_WORKSPACE) workspace
	terraform plan $(VAR_FILES)

out: init
	@echo planning changes to the $(TF_WORKSPACE) workspace
	terraform plan $(VAR_FILES) -out $(OUTFILE_PATH) -no-color | tee $(OUTFILE_PATH).txt

outapply:
	terraform apply $(OUTFILE_PATH)

output:
	@terraform output

apply: init
	@echo applying changes to the $(WORKSPACE) workspace
	terraform apply $(VAR_FILES)

fapply:
	@echo applying changes to the $(WORKSPACE) workspace
	terraform apply $(VAR_FILES)

autoapply: init
	@echo applying changes to the $(WORKSPACE) workspace
	terraform apply $(VAR_FILES) -auto-approve

destroy: init
	@echo applying changes to the $(WORKSPACE) workspace
	terraform destroy $(VAR_FILES)

autodestroy: init
	@echo applying changes to the $(WORKSPACE) workspace
	terraform apply -destroy -auto-approve $(VAR_FILES)

new: init
	@echo "create a new terraform workspace by running 'make NEW=my-new-name new'"
	$(shell [ -z $(NEW) ] && echo 'please define the NEW env var'; exit 1;)
	terraform workspace new $(NEW)
	echo "env = \"$(NEW)\"" >> $(NEW).tfvars

deploy-dashboard:
	aws cloudwatch put-dashboard \
		--dashboard-name serverless-aws-python3-fec-datasync-dashboard \
		--dashboard-body file://cloudwatch.json

