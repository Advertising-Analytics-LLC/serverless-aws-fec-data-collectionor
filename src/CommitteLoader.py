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
from src import JSONType
from src.database import Database
from datetime import datetime, timedelta
from time import time
from typing import List, Dict, Any
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.serialization import serialize_dates


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', 'committee-sync-queue')

# LOGGING
logger = logging.getLogger(__name__)

# BUSYNESS LOGIC
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

def pull_message_from_sqs() -> Dict[str, Any]:
    """pulls a committee id from SQS
    see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message

    Returns:
        Any: SQS Message object
    """

    message = queue.receive_messages(MaxNumberOfMessages=1)
    if not message:
        logger.info('No messages received, exiting')
        exit(0)

    return message[0]

def get_committee_data(committee_id: str) -> JSONType:
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

def write_committee_data(committee_data: JSONType):
    """opens DB contextmanager and upserts committee data

    Args:
        committee_data (JSONType): CommitteeDetail object from OpenFEC API
    """
    with Database() as db_obj:
        db_obj.upsert_committeedetail(committee_data)

def committeLoader(event: dict, context: object):
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift
        and loops like that for ten minutes
    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """

    start_time = time()
    time_to_end = start_time + 60 * 10
    logger.info(f'Running committeeLoader from now until {time_to_end}')

    while time() < time_to_end:
        message = pull_message_from_sqs()
        committee_id = message.body
        committee_data = get_committee_data(committee_id)

        if not committee_data:
            logger.error(f'Committee {committee_id} not found! exiting.')
            exit(1)

        write_committee_data(committee_data[0])
        message.delete()

    if time() > time_to_end:
        minutes_ran = (time() - start_time) / 60
        logger.warn(f'committeeLoader ended late at {minutes_ran} ')
