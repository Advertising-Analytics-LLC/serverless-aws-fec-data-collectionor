#!/bin/env python3

import boto3
import json
import logging
import os
from datetime import datetime, timedelta
from src import logger
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name


API_KEY = get_param_value_by_name(os.environ['API_KEY'])
MIN_LAST_F1_DATE = os.getenv('MIN_LAST_F1_DATE', datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d'))

sqs = boto3.resource('sqs')
SQS_QUEUE_NAME = os.environ['SQS_QUEUE_NAME']
logger.debug(f'using queue: {SQS_QUEUE_NAME}')
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)


def push_committee_id_to_sqs(message_list):
    """Pushes a list of committee_ids to SQS"""

    for msg in message_list:
        response = queue.send_message(MessageBody=msg['committee_id'])
        logger.debug(response)


def get_committees_since(isodate: str, max_last_f1_date='') -> json:
    """gets list of committees that have filed between two dates

    Args:
        isodate: date in isoformat YYYY-MM-DD
        max_last_f1_date: date in isoformat YYYY-MM-DD

    Returns:
        json: json list containing IDs
    """

    # only get those filed today
    if max_last_f1_date:
        get_committees_payload = {'min_last_f1_date': isodate, 'max_last_f1_date': max_last_f1_date}
    else:
        get_committees_payload = {'min_last_f1_date': isodate}
    results_json = []
    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_route_paginator('/committees/', payload=get_committees_payload)
    for response in response_generator:
        results_json += response['results']
    return results_json


def committeSync(event: dict, context: object):
    """Gets committees who've filed in the last day and push their IDs to SQS"""

    logger.info(f'Running committeeSync with date: {MIN_LAST_F1_DATE}')
    results_json = get_committees_since(MIN_LAST_F1_DATE)
    if not results_json:
        logger.warning('no results')
        return {}
    response = push_committee_id_to_sqs(results_json)
    logging.debug(response)


def lambdaBackfillHandler(event: dict, context: object):
    """Gets committees who've filed in the last day and push their IDs to SQS"""

    from src.backfill import get_next_day, filings_backfill_success, filings_sync_backfill_date

    MIN_LAST_F1_DATE = filings_sync_backfill_date('commmittee_file_date')
    max_last_f1_date = get_next_day(MIN_LAST_F1_DATE)

    logger.info(f'Running committeeSync with date: {MIN_LAST_F1_DATE}')
    results_json = get_committees_since(MIN_LAST_F1_DATE, max_last_f1_date)
    if not results_json:
        logger.warning('no results')
    else:
        response = push_committee_id_to_sqs(results_json)
        logging.debug(response)

    filings_backfill_success(MIN_LAST_F1_DATE, 'commmittee_file_date')
