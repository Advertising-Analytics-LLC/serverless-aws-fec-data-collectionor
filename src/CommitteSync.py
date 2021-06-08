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
from src import logger, serialize_dates
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import push_committee_id_to_sqs


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
MIN_LAST_F1_DATE = os.getenv('MIN_LAST_F1_DATE', datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d'))

# BUSYNESS LOGIC
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
    response_generator = openFec.get_route_paginator('/committees/',
                                                    payload=get_committees_payload)
    for response in response_generator:
        results_json += response['results']
    return results_json


def committeSync(event: dict, context: object) -> List[any]:
    """Gets committees who've filed in the last day and push their IDs to SQS

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """

    logger.info(f'Running committeeSync with date: {MIN_LAST_F1_DATE}')
    results_json = get_committees_since(MIN_LAST_F1_DATE)
    if not results_json:
        logger.warning('no results')
        return {}
    response = push_committee_id_to_sqs(results_json)
    logging.debug(response)
    return response


def lambdaBackfillHandler(event: dict, context: object) -> List[any]:
    """Gets committees who've filed in the last day and push their IDs to SQS

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """

    from src.backfill import committee_sync_backfill_date, get_next_day

    MIN_LAST_F1_DATE = committee_sync_backfill_date()
    max_last_f1_date = get_next_day(MIN_LAST_F1_DATE)

    logger.info(f'Running committeeSync with date: {MIN_LAST_F1_DATE}')
    results_json = get_committees_since(MIN_LAST_F1_DATE, max_last_f1_date)
    if not results_json:
        logger.warning('no results')
        return {}
    response = push_committee_id_to_sqs(results_json)
    logging.debug(response)

    return response
