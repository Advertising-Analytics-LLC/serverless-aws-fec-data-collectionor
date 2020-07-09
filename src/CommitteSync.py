#!/bin/env python3
"""
CommitteeSync lambda:
iterates on /committees API and publishes committee IDs to a queue thing.
It should:
- read the last filing date scanned parameter ()
- query for only committees updated in the 24 hours prior (just to make sure we don't miss anything)
"""

import boto3
import datetime
import json
import logging
import os
from typing import List
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.serialization import serialize_dates


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', 'committee-sync-queue')

# LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', logging.DEBUG))

for handler in logger.handlers:
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s](%(name)s) %(message)s'))

# BUSYNESS LOGIC
def get_todays_committees() -> json:
    """gets list of committees that have filed today

    Returns:
        json: json list containing results
    """
    # only get those filed today
    todays_date = datetime.date.today().isoformat()
    get_committees_payload = {'min_last_f1_date': todays_date}
    results_json = []
    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_committees_paginator(get_committees_payload)
    for response in response_generator:
        results_json += response['results']
    return results_json

def push_them_to_sqs(message_list: List[str]) -> object:
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    response = queue.send_response(Entries=message_list)
    print('type(response)')
    print(type(response))
    print('response')
    print(response)
    return response

def committeSync(event, context):
    """

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """
    results_json = get_todays_committees()
    response = push_them_to_sqs(results_json)
    return response
