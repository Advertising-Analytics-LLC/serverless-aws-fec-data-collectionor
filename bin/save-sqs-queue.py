#!/usr/bin/env python3

import argparse
import boto3
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser(
    description='Saves all messages from an AWS SQS queue into a folder.')

parser.add_argument(
    '-q', '--queue-url', dest='queue_url', type=str, required=True,
    help='The name of the AWS SQS queue to save.')

parser.add_argument(
    '-o', '--output', dest='output', type=str, default='queue-messages',
    help='The output folder for saved messages.')

parser.add_argument(
    '-d', '--delete', dest='delete', default=False, action='store_true',
    help='Whether or not to delete saved messages from the queue.')

parser.add_argument(
    '-v', '--visibility', dest='visibility', type=int, default=60,
    help='The message visibility timeout for saved messages.')

args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

client = boto3.client('sqs')

count = 0
while True:
    response = client.receive_message(
        QueueUrl=args.queue_url,
        MaxNumberOfMessages=10,
        AttributeNames=['ApproximateFirstReceiveTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=args.visibility
    )

    messages = response.get('Messages')

    if not messages or len(messages) == 0:
        break

    for msg in messages:
        d = int(msg['Attributes']['ApproximateFirstReceiveTimestamp'])/1000
        d = datetime.fromtimestamp(d)
        path = os.path.join(args.output, d.strftime('%Y-%m-%d'))
        if not os.path.exists(path):
            os.mkdir(path)
        filename = os.path.join(path, msg['MessageId'])
        obj = {'id': msg['MessageId'],
               'attributes': msg.get('MessageAttributes'),
               'body': msg['Body']}

        with open(filename, 'w') as f:
            json.dump(obj, f, indent=2)
            count += 1
            print(f'Saved message to {filename}')
            if args.delete:
                client.delete_message(QueueUrl=args.queue_url, ReceiptHandle=msg['ReceiptHandle'])

print(f'{count} messages saved')
