#!/bin/bash -e
#
# script to deploy
# creates infra through cfn
# and deploys all serverless functions

version="v0.0.1"
git_describe_tag=$(git describe --always --dirty --match 'NOT A TAG')

stack_name="fec-datasync-resources"

echo 'deploying cloudformation stack'
aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --stack-name "${stack_name}" \
    --parameters Version="${version}-${git_describe_tag}"
    --template prerequisite-cloudformation-resources.yml

echo 'the serverless.yml should be updated with these values'
aws cloudformation describe-stacks --stack-name fec-datasync-resources | jq '.Stacks[0].Outputs'

echo 'deploying serverless function'
serverless deploy
