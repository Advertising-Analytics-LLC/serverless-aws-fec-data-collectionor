SHELL := /bin/bash

.phony: login
login:
	aws_okta_login advertisinganalytics-admin-okta

.phony: test
test:
	sls invoke local -f CommitteeSync

.phony: deploy
deploy:
	sls deploy

.phony: run
run:
	sls invoke -f CommitteeSync
