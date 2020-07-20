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
from copy import deepcopy
from requests import Response
from time import asctime, gmtime, time
from typing import Any, Dict, List
from src import JSONType, logger, schema
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import pull_message_from_sqs


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

# BUSYNESS LOGIC

def parse_message(message: JSONType) -> Dict[str, str]:
    """parse string from sqs - it's kind of jsonish

    Args:
        message (JSON): almost json

    Returns:
        Dict[str, str]: python dictionary
    """

    msg_body = json.loads(message.body)
    body_content = json.loads(msg_body['Message'].replace("'", '"'))

    return body_content


def get_filings(filters: Dict[str, str]) -> Dict[str, Any]:
    """pulls filings from openfec api

    Args:
        filters (Dict[str, str]): filters for API query

    Returns:
        Dict[str, Any]: response as a dict
    """

    path = '/filings/'
    reports = []
    openFec = OpenFec(API_KEY)
    for report in  openFec.get_route_paginator(path, filters):
        results = report['results']
        if results:
            reports.append(results)

    return reports


def get_totals(committee_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """[summary]

    Args:
        committee_id (str): [description]
        filters (Dict[str, Any]): [description]

    Returns:
        [type]: [description]
    """

    totals_path = '/committee/' + committee_id + '/totals/'
    totals = []
    openFec = OpenFec(API_KEY)
    for report in openFec.get_route_paginator(totals_path, filters):
        results = report['results']
        if results:
            totals.append(results)

    return totals

def get_filings_and_totals(committee_id: str) -> List[Dict[str, Any]]:
    """gets filings and totals for committee

    Args:
        committee_id (str): ID of committee. eg C01234567

    Returns:
        List[Dict[str, Any]]: List of responses
    """
    filters = {
        'committee_id': committee_id,
        'cycle': '2020', #fallback_cycle if cycle_out_of_range else cycle, # TODO: ?
        'per_page': 1,
        'sort_hide_null': True,
        'most_recent': True,
        'form_category': 'REPORT'
    }
    filings = get_filings(deepcopy(filters))
    totals = get_totals(committee_id, deepcopy(filters))
    return filings, totals

def upsert_amendment_chain(filing_id: str, amendment_chain: List[str]):
    pass

def upsert_filing(filing: JSONType):
    """just dynamicaly generate the query

    Args:
        filing (JSONType): A dictionary representing a single filing record
    """
    pk = filing['fec_file_id']
    amendment_chain = filing.pop('amendment_chain')
    upsert_amendment_chain(pk, amendment_chain)
    filing_exists_query = schema.fec_file_exists(pk)
    with Database() as db:
        if db.record_exists(filing_exists_query):
            query = schema.insert_fec_filing(filing)
        else:
            query = schema.update_fec_filing(filing)
        db.query(query)


def upsert_filings(filings_list: JSONType):
    for filing in filings_list:
        upsert_filing(filing)


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    start_time = time()
    minutes_to_run = 10
    time_to_end = start_time + 60 * minutes_to_run
    logger.debug(f'running {__file__} for {minutes_to_run}, from now until {asctime(gmtime(time_to_end))}')
    logger.debug(event)

    while time() < time_to_end:
        message = pull_message_from_sqs()
        if not message:
            return
        message_parsed = parse_message(message)
        committee_id = message_parsed['committee_id']

        filings, totals = get_filings_and_totals(committee_id)

        # filing is list of lists, flatten it
        filings_flat = [item for sublist in filings for item in sublist]
        upsert_filings(filings_flat)
        message.delete()

    if time() > time_to_end:
        minutes_ran = (time() - start_time) / 60
        logger.warn(f'committeeLoader ended late at {minutes_ran} ')

    return True
