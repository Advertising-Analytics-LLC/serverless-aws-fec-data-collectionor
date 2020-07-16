#!/bin/bash -e
#
# script to deploy
# creates infra through cfn
# and deploys all serverless functions

source bin/get-version.sh
version_tag=$(get_version)
echo "Version=$version_tag"


stack_name="fec-datasync-resources"

echo 'deploying cloudformation stack'
aws cloudformation deploy \
    --no-fail-on-empty-changeset \
    --stack-name "${stack_name}" \
    --parameter-overrides 'Version='"${version_tag}" \
    --template-file prerequisite-cloudformation-resources.yml

echo 'the serverless.yml should be updated with these values'
aws cloudformation describe-stacks --stack-name fec-datasync-resources | jq '.Stacks[0].Outputs'

echo 'deploying serverless function'
Version="${version_tag}" serverless deploy
