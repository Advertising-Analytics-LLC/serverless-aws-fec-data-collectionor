#!/bin/bash -e


stack_name="fec-datasync-resources"

echo 'deploying cloudformation stack'
aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --stack-name "${stack_name}" \
    --template prerequisite-cloudformation-resources.yml

echo 'the serverless.yml should be updated with these values'
aws cloudformation describe-stacks --stack-name fec-datasync-resources | jq '.Stacks[0].Outputs'

echo 'deploying serverless function'
sls deploy
