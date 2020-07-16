#!/bin/bash -e


change_set_name="`whoami`-`date +%F-%H-%M-%S`"
stack_name="fec-datasync-resources"

echo 'creating cloudformation change set'
aws cloudformation create-change-set \
    --change-set-name "${change_set_name}" \
    --stack-name "${stack_name}" \
    --template-body file://$(pwd)/prerequisite-cloudformation-resources.yml

echo 'describing cloudformation change set'
aws cloudformation describe-change-set \
    --change-set-name "${change_set_name}" \
    --stack-name "${stack_name}"

echo 'apply changes? (y/n)'
read yes_or_no
if [ $yes_or_no == 'y' ]; then
    echo 'applying changes'
    bin/deploy.sh
    exit 0
fi

echo 'deleting cloudformation change set'
aws cloudformation delete-change-set \
    --change-set-name "${change_set_name}" \
    --stack-name "${stack_name}"


# echo 'the serverless.yml should be updated with these values'
# aws cloudformation describe-stacks --stack-name fec-datasync-resources | jq '.Stacks[0].Outputs'

# echo 'deploying serverless function'
# sls deploy
