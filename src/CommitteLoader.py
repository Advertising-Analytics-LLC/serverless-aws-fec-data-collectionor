#!/bin/env python3
"""
CommitteeLoader lambda:
CommitteeLoader lambda that subscribes to topic, read committee IDs from queue, and loads data from the /committees/COMMITTEE_ID API
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
if not API_KEY or not SQS_QUEUE_NAME:
    logging.error('missing variable API_KEY or SQS QUEUE NAME')

# LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', logging.DEBUG))
logger.debug('hello world')


# BUSYNESS LOGIC

def pull_committee_ids_from_sqs() -> object:
    """

    Returns:
        object: [description]
    """
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    for message in queue.receive_messages():
        # process msg
        pass
    pass

def committeLoader(event: dict, context: object) -> List[any]:
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """
    logger.debug(f'Running committeeLoader')
    pull_committee_ids_from_sqs()
    pass
