#!/bin/env python3
"""
CommitteeLoader lambda:
- subscribes to topic,
- read committee IDs from queue,
- gets data from the /committees/COMMITTEE_ID API
- writes data to redshift
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

# BUSYNESS LOGIC

def pull_committee_id_from_sqs() -> str:
    """pulls a committee id from SQS

    Returns:
        str: committee_id
    """
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    message = queue.receive_messages(MaxNumberOfMessages=1)
    if not message:
        logger.warning('No messages recieved, exiting')
        exit(0)
    committee_id = message[0].body
    logger.debug(f'Pulled committee ID {committee_id}')
    return committee_id

def get_committee_data(committee_id: str) -> json:
    """Pulls the committee data from the openFEC API
        https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__

    Args:
        committee_id (str): ID of committee

    Returns:
        json: committee data
    """
    results_json = []
    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_committee_by_id_paginator(committee_id)
    for response in response_generator:
        results_json += response['results']
    return results_json

def transform_committee_data(committee_data: json):
    pass

def write_committee_data(committee_data: json):
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
    committee_id = pull_committee_id_from_sqs()
    committee_data = get_committee_data(committee_id)
    return committee_data
