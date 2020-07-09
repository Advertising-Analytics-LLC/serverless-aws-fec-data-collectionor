#!/bin/env python3
"""
CommitteeSync lambda:
iterates on /committees API and publishes committee IDs to a queue thing.
It should:
- read the last filing date scanned parameter ()
- query for only committees updated in the 24 hours prior (just to make sure we don't miss anything)
"""

import datetime
import json
import logging
import os
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.serialization import serialize_dates


API_KEY = get_param_value_by_name('/global/openfec-api/api_key')

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', logging.DEBUG))

for handler in logger.handlers:
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s](%(name)s) %(message)s'))

def committeSync(event, context):
    """

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """
    # only get those filed today
    # todays_date = datetime.date.today().isoformat()
    todays_date = '2019-01-01'
    get_committees_payload = {'min_last_f1_date': todays_date}
    response_json = []

    openFec = OpenFec(API_KEY)
    # response_json = openFec.get_committees(get_committees_payload)
    response_generator = openFec.get_committees_paginator(get_committees_payload)
    for response in response_generator:
        response_json.append(response)

    response = {
        'statusCode': 200,
        'body': response_json
    }

    return response
