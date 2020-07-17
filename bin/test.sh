#!/bin/bash

shopt -s expand_aliases
alias slif="serverless invoke local --function"

pytest

slif CommitteeSync
slif CommitteeLoader
slif RSSSubscriber
slif FilingWriter
