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
from datetime import datetime
from collections import OrderedDict
from psycopg2.sql import SQL, Literal
from requests import Response
from time import asctime, gmtime, time
from typing import Any, Dict, List
from src import condense_dimension, get_current_cycle_year, JSONType, logger
from src.database import Database, get_insert_query
from src.OpenFec import OpenFec, NotFound404Exception
from src.secrets import get_param_value_by_name
from src.sqs import delete_message_from_sqs, parse_message


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

# comittee totals

def committee_total_exists(committee_id: str, cycle: int) -> SQL:
    query = SQL('SELECT * FROM fec.committee_totals WHERE committee_id={committee_id} AND cycle={cycle}')\
        .format(committee_id=Literal(committee_id), cycle=Literal(cycle))
    return query


def insert_committee_total(committee_total: JSONType) -> SQL:
    table = 'fec.committee_totals'
    query = get_insert_query(table, committee_total)
    return query


def update_committee_total(committee_total: JSONType) -> SQL:

    committee_id = committee_total.pop('committee_id')
    cycle = committee_total.pop('cycle')

    values = OrderedDict(sorted(committee_total.items()))
    query_string = 'UPDATE fec.committee_totals SET ' \
        + ', '.join([f' {key}={{}}' for key, val in values.items()])\
        + ' WHERE committee_id={}'\
        + ' AND cycle={}'

    query = SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()], Literal(committee_id), Literal(cycle))

    return query

#
# fec file

def fec_file_exists(fec_file_id: str) -> SQL:
    query = SQL('SELECT * FROM fec.filings WHERE fec_file_id={fec_file_id}')\
        .format(fec_file_id=Literal(fec_file_id))
    return query


def insert_fec_filing(filing: JSONType) -> SQL:
    table = 'fec.filings'
    query = get_insert_query(table, filing)
    return query


def amendment_chain_exists(fec_file_id: str, amendment_id: str) -> SQL:
    query = SQL('SELECT * FROM fec.filing_amendment_chain WHERE fec_file_id={} AND amendment_id={}')\
        .format(Literal(int(fec_file_id)), Literal(int(amendment_id)))
    return query


def insert_amendment_chain(fec_file_id: str, amendment_id: str, amendment_number: int) -> SQL:
    query = SQL('INSERT INTO fec.filing_amendment_chain(fec_file_id, amendment_id, amendment_number) VALUES ({}, {}, {})')\
        .format(Literal(fec_file_id), Literal(int(amendment_id)), Literal(int(amendment_number)))
    return query


# BUSYNESS LOGIC

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

def upsert_amendment_chain(filing_id: str, amendment_chain: List[str]):
    """upserts amendment chain linker table

    Args:
        filing_id (str): ID of filing
        amendment_chain (List[str]): list of amendment ids
    """

    amendment_number = 0
    for amendment in amendment_chain:
        with Database() as db:
            if not db.record_exists(amendment_chain_exists(filing_id, amendment)):
                query = insert_amendment_chain(filing_id, amendment, amendment_number)
                db.try_query(query)
            amendment_number += 1


def upsert_filing(filing: JSONType) -> bool:
    """upserts single filing record

    Args:
        filing (JSONType): A dictionary representing a single filing record

    Returns:
        bool: success
    """

    fec_file_id = filing['fec_file_id']

    if not fec_file_id or fec_file_id is 'None':
        logger.warning(f'fec_file_id missing, filing: {filing}')
        return False

    fec_file_id = fec_file_id.replace('FEC-', '')
    filing['fec_file_id'] = fec_file_id
    filing = condense_dimension(filing, 'additional_bank_names')

    amendment_chain = filing.pop('amendment_chain')
    if amendment_chain:
        upsert_amendment_chain(fec_file_id, amendment_chain)

    with Database() as db:
        if db.record_exists(fec_file_exists(fec_file_id)):
            logger.warning(f'Financial Summary with fec_file_id {fec_file_id} already exists')
            return True

        else:
            query = insert_fec_filing(filing)

        return db.try_query(query)


def upsert_committee_total(commitee_total: JSONType) -> bool:
    """upserts single commitee total given as dict/json

    Args:
        filing (JSONType): A dictionary representing a single committee total record

    Returns:
        bool: success
    """
    pk1 = commitee_total['committee_id']
    pk2 = commitee_total['cycle']

    with Database() as db:
        if db.record_exists(committee_total_exists(pk1, pk2)):
            query = update_committee_total(commitee_total)
        else:
            query = insert_committee_total(commitee_total)

        success = db.try_query(query)
        return success


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Success
    """

    logger.debug(f'running {__file__}')
    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:

        message_parsed = parse_message(message)
        committee_id = message_parsed['committee_id']

        # Get for current cycle
        current_cycle_year = get_current_cycle_year()
        filters = {
            'committee_id': committee_id,
            'cycle': current_cycle_year,
            'per_page': 1,
            'sort_hide_null': True,
            'most_recent': True,
            'form_category': 'REPORT'
        }

        try:
            filings = get_filings(deepcopy(filters))
            totals = get_totals(committee_id, deepcopy(filters))
        except NotFound404Exception as e:
            logger.warning(f'{e} query filters: {filters}')
            continue

        # handle fec.filings
        # filing is list of lists, flatten it
        filings_flat = [item for sublist in filings for item in sublist]
        for filing in filings_flat:
            upsert_filing(filing)

        # handle fec.committee_totals
        # totals is list of lists, flatten it
        totals_flat = [item for sublist in totals for item in sublist]
        for committee_total in totals_flat:
            upsert_committee_total(committee_total)

    return True
