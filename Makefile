SHELL := /bin/bash

.phony: setup
setup:
	@echo make sure you've installed python3 and npm as explained in the README
	bin/dev-setup.sh

.phony: login
login:
	aws_okta_login advertisinganalytics-admin-okta

.phony: test
test:
	sls invoke local -f CommitteeSync

.phony: deploy
deploy:
	bin/deploy.sh

.phony: run
run:
	sls invoke -f CommitteeSync
