#!/bin/env python3
"""
CandidateSync lambda:
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List
from src import JSONType, logger, schema
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import delete_message_from_sqs, push_message_to_sqs


API_KEY = get_param_value_by_name(os.environ['API_KEY'])
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', '')
MIN_FIST_FILE_DATE = os.getenv('MIN_FIST_FILE_DATE', datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d'))


# business logic

def get_candidates_since(isodate: str) -> json:
    """gets list of candidates that have filed today

    Args:
        isodate: date in isoformat YYYY-MM-DD

    Returns:
        json: json list containing IDs
    """

    logger.debug(f'Querying for Candidates who file after {isodate}')

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
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    logger.debug(f'running {__file__}')

    candidates_list = get_candidates_since(MIN_FIST_FILE_DATE)

    for candidate in candidates_list:
        push_message_to_sqs(candidate)

    return True

def lambdaBackfillHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    logger.debug(f'running {__file__}')

    from src.backfill import candidate_sync_backfill_date
    MIN_FIST_FILE_DATE = candidate_sync_backfill_date()

    candidates_list = get_candidates_since(MIN_FIST_FILE_DATE)

    for candidate in candidates_list:
        push_message_to_sqs(candidate)

    return True
