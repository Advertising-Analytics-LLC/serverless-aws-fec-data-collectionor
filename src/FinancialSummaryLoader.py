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


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

# BUSYNESS LOGIC

def parse_events(event: JSONType) -> List[Dict[str, Any]]:
    """takes the raw event from AWS Lambda and parses into a list of messages

    Args:
        event (JSONType): List of SQS Message events
            see https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html

    Returns:
        List[Dict[str, Any]]: List of message bodies
    """

    message_body_list = []
    records = event['Records']
    for record in records:
        my_body = record['body']
        json_body = json.loads(my_body)
        message_body_list.append(json_body)

    return message_body_list


def parse_message(message: JSONType) -> Dict[str, str]:
    """parse string from sqs - it's kind of jsonish

    Args:
        message (JSON): almost json

    Returns:
        Dict[str, str]: python dictionary
    """

    body_content = json.loads(message['Message'].replace("'", '"'))

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
    """upserts amendment chain linker table

    Args:
        filing_id (str): ID of filing
        amendment_chain (List[str]): list of amendment ids
    """

    amendment_number = 0
    for amendment in amendment_chain:
        amendment_chain_exists_query = schema.amendment_chain_exists(filing_id, amendment)
        with Database() as db:
            if not db.record_exists(amendment_chain_exists_query):
                query = schema.insert_amendment_chain(filing_id, amendment, amendment_number)
                db.query(query)
            amendment_number += 1


def upsert_filing(filing: JSONType):
    """upserts single filing record

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
    """loops over filing records and upserts into db

    Args:
        filings_list (JSONType): list of filings as json/dict
    """
    for filing in filings_list:
        upsert_filing(filing)


def upsert_committee_total(commitee_total: JSONType):
    """upserts single commitee total given as dict/json

    Args:
        filing (JSONType): A dictionary representing a single committee total record
    """
    pk1 = commitee_total['committee_id']
    pk2 = commitee_total['cycle']

    total_exists_query = schema.committee_total_exists(pk1, pk2)
    with Database() as db:
        if db.record_exists(total_exists_query):
            query = schema.insert_committee_total(commitee_total)
        else:
            query = schema.update_committee_total(commitee_total)
        db.query(query)


def upsert_committee_totals(commitee_total_list: JSONType):
    """loops over list of committee totals records

    Args:
        commitee_total_list (JSONType): record as list of json/dicts
    """
    for committee_total in commitee_total_list:
        upsert_committee_total(committee_total)


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

    messages = parse_events(event)

    for message in messages:

        message_parsed = parse_message(message)
        committee_id = message_parsed['committee_id']

        filings, totals = get_filings_and_totals(committee_id)

        # filing is list of lists, flatten it
        filings_flat = [item for sublist in filings for item in sublist]
        upsert_filings(filings_flat)

        # filing is list of lists, flatten it
        totals_flat = [item for sublist in totals for item in sublist]
        upsert_committee_totals(totals_flat)



    return True
