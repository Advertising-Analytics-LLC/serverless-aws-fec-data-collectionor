#!/bin/env python3


import json
import os
from datetime import datetime, timedelta
from src import logger
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import push_message_to_sqs


API_KEY = get_param_value_by_name(os.environ['API_KEY'])
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', '')
MIN_FIST_FILE_DATE = os.getenv('MIN_FIST_FILE_DATE', datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d'))


def get_candidates_since(isodate: str, max_first_file_date='') -> json:
    """gets list of candidates that have filed today

    Args:
        isodate: date in isoformat YYYY-MM-DD

    Returns:
        json: json list containing IDs
    """

    logger.debug(f'Querying for Candidates who file after {isodate}')

    if max_first_file_date:
        get_candidates_payload = {'min_first_file_date': isodate, 'max_first_file_date': max_first_file_date}
    else:
        get_candidates_payload = {'min_first_file_date': isodate}

    openFec = OpenFec(API_KEY)

    response_generator = openFec.get_route_paginator(
                                '/candidates/',
                                get_candidates_payload)

    results_json = []
    for response in response_generator:
        results_json += response['results']

    return results_json


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html"""

    candidates_list = get_candidates_since(MIN_FIST_FILE_DATE)

    for candidate in candidates_list:
        push_message_to_sqs(candidate)

    return True


def lambdaBackfillHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html"""

    from src.backfill import get_next_day, filings_backfill_success, filings_sync_backfill_date

    MIN_FIST_FILE_DATE = filings_sync_backfill_date('candidate_file_date')
    max_first_file_date = get_next_day(MIN_FIST_FILE_DATE)

    candidates_list = get_candidates_since(MIN_FIST_FILE_DATE, max_first_file_date)

    for candidate in candidates_list:
        push_message_to_sqs(candidate)

    filings_backfill_success(MIN_FIST_FILE_DATE, 'candidate_file_date')

    return True
