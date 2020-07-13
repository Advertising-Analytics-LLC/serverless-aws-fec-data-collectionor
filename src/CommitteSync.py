#!/bin/env python3
"""
CommitteeSync lambda:
iterates on /committees API and publishes committee IDs to a queue thing.
It should:
- read the last filing date scanned parameter ()
- query for only committees updated in the 24 hours prior (just to make sure we don't miss anything)
"""

import boto3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.serialization import serialize_dates


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', 'committee-sync-queue')

# LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', logging.DEBUG))
logger.debug('hello world')


# BUSYNESS LOGIC
def get_committees_since(isodate: str) -> json:
    """gets list of committees that have filed today

    Args:
        isodate: date in isoformat YYYY-MM-DD

    Returns:
        json: json list containing IDs
    """
    # only get those filed today
    get_committees_payload = {'min_last_f1_date': isodate}
    results_json = []
    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_committees_paginator(get_committees_payload)
    for response in response_generator:
        results_json += response['results']
    return results_json

def push_committee_id_to_sqs(message_list: List[any]) -> object:
    """Pushes a list of SendMessageBatchRequestEntry (messages) to
        see https://github.com/boto/botocore/blob/f1f0c6d2e445d7c3a3f8f355eaf6d692bbf3cd6a/botocore/data/sqs/2012-11-05/service-2.json#L1238
    Args:
        message_list (List[SendMessageBatchRequestEntry]): [description]

    Returns:
        object: [description]
    """
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    responses = []
    for msg in message_list:
        response = queue.send_message(
            MessageBody=json.dumps(msg['committee_id']))
        logger.debug(response)
        responses.append(response)
    return responses

def committeSync(event: dict, context: object) -> List[any]:
    """Gets committees who've filed in the last day and push their IDs to SQS

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """
    todays_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    logger.debug(f'Running committeeSync with date: {todays_date}')
    results_json = get_committees_since(todays_date)
    if not results_json:
        logger.warning('no results')
        return {}
    response = push_committee_id_to_sqs(results_json)
    logging.debug(response)
    return response
