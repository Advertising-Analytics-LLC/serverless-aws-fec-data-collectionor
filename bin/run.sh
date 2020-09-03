#!/bin/bash -x

shopt -s expand_aliases
alias slif="serverless invoke --function"

for func in CommitteeSync CandidateSync FilingSync
do
    slif $func
done
