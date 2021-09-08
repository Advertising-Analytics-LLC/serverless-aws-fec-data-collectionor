#!/usr/bin/env python

'''
sends each line of a text file to ingest queue
run:
	bin/enqueue-committees.py	<FILE_NAME>
eg:
	bin/enqueue-committees.py ./Missing-committee_details-8.31.21.csv

where ./Missing-committee_details-8.31.21.csv is a files containing committee IDs seperated by newlines
'''

import boto3
import json
# import subprocess
import sys


args = sys.argv
args.pop(0)
txt_files = args

sqs = boto3.resource('sqs')
SQS_QUEUE_NAME = 'committee-sync-queue'
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)


def process_file(txt_file):
	with open(txt_file, 'r') as fh:
		for line in fh:
			line = line.strip()
			print(f'Sending {line} to {SQS_QUEUE_NAME}')
			queue.send_message(MessageBody=line)


for tfile in txt_files:
	print(f'processing {tfile}')
	process_file(tfile)
