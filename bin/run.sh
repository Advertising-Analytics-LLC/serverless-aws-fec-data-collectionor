#!/bin/bash

shopt -s expand_aliases
alias slif="serverless invoke --function"

slif CommitteeSync
slif CommitteeLoader
slif RSSSubscriber
slif FilingWriter
