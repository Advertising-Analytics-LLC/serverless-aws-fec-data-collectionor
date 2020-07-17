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
from src import JSONType, logger
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import pull_message_from_sqs


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

# BUSYNESS LOGIC
openFec = OpenFec(API_KEY)


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
    reports = openFec.get_route(path, filters)

    # (4)call committee/{committee_id}/totals? under tag:financial
    # get financial totals
    path = '/committee/' + committee_id + '/totals/'
    totals = openFec.get_route(path, filters)

    return reports, totals

def lambdaHandler(event: dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """
    logger.debug(f'running {__file__}')
    logger.debug(event)

    sqs_message = pull_message_from_sqs()
    logger.debug(sqs_message)
