#!/bin/python

import argparse
import boto3
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser(
    description='places a list of committee ids seperated by newlines into the committee-sync-queue SQS queue')

parser.add_argument(
    '-q', '--queue-url', dest='queue_url', type=str, required=True,
    help='The name of the AWS SQS queue')

parser.add_argument(
    '-f', '--file', dest='file', type=str, required=True,
    help='The file of candidate IDs')

args = parser.parse_args()
client = boto3.client('sqs')

lines = []

with open(args.file, 'r') as fh:
    for line in fh.readlines():
        line = line.replace(' ', '')
        line = line.replace('\n', '')
        if line:
            theline = line
            lines.append(theline)

print(len(lines))

for line in lines:
    response = client.send_message(
        QueueUrl=args.queue_url,
        MessageBody=json.dumps({ 'candidate_id': line})
    )
    print(response)
