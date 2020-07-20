#!/bin/env python3
"""
FilingWriter lambda:
- subscribes to topic,
- read committee IDs from queue,
- gets data from the /committees/COMMITTEE_ID API
- writes data to redshift
"""

import boto3
import json
import os
from requests import Response
from time import time
from typing import Dict
from src import JSONType, logger
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import pull_message_from_sqs


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

# BUSYNESS LOGIC
openFec = OpenFec(API_KEY)


def parse_message(message: Response) -> Dict[str, str]:
    msg_body = json.loads(message.body)
    body_content = json.loads(msg_body['Message'].replace("'", '"'))
    return body_content

def load_reports_and_totals(committee_id):
    filters = {
        'committee_id': committee_id,
        'cycle': '2020', #fallback_cycle if cycle_out_of_range else cycle,
        'per_page': 1,
        'sort_hide_null': True,
        'most_recent': True,
        'form_category': 'REPORT'
    }

    # (3) call /filings? under tag:filings
    # get reports from filings endpoint filter by form_category=REPORT
    path = '/filings/'
    reports = []
    for report in  openFec.get_route_paginator(path, filters):
        reports.append(report)

    # (4)call committee/{committee_id}/totals? under tag:financial
    # get financial totals
    path = '/committee/' + committee_id + '/totals/'
    totals = []
    for report in openFec.get_route_paginator(path, filters):
        totals.append(report)

    return reports, totals

def lambdaHandler(event: dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    start_time = time()
    time_to_end = start_time + 60 * 10
    logger.debug(f'running {__file__} from now until {time_to_end}')

    while time() < time_to_end:
        message = pull_message_from_sqs()
        if not message:
            return
        message_parsed = parse_message(message)
        committee_id = message_parsed['committee_id']
        committee_data = load_reports_and_totals(committee_id)

        if not committee_data:
            logger.error(f'Committee {committee_id} not found! exiting.')
            return False

        logger.debug(committee_data)
        # write_committee_data(committee_data[0])
        # message.delete()

    if time() > time_to_end:
        minutes_ran = (time() - start_time) / 60
        logger.warn(f'committeeLoader ended late at {minutes_ran} ')

    return True
