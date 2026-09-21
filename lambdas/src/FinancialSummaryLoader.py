#!/bin/env python3
"""
FilingWriter lambda:
- subscribes to topic,
- read committee IDs from queue,
- gets data from the /committees/COMMITTEE_ID API
- writes data to redshift
"""

import json
import os
import uuid
from copy import deepcopy
from psycopg2.sql import SQL, Literal
from typing import Any, Dict, List, Tuple
from src import condense_dimension, get_current_cycle_year, JSONType, logger
from src.database import Database
from src.OpenFec import OpenFec, NotFound404Exception
from src.secrets import get_param_value_by_name
from src.sqs import parse_message


API_KEY = get_param_value_by_name(os.environ['API_KEY'])


def committee_total_exists(committee_id: str, cycle: int) -> SQL:
    query = SQL('SELECT * FROM fec.committee_totals WHERE committee_id={committee_id} AND cycle={cycle}')\
        .format(committee_id=Literal(committee_id), cycle=Literal(cycle))
    return query


#
# fec file

def fec_file_exists(fec_file_id: str) -> SQL:
    query = SQL('SELECT * FROM fec.filings WHERE fec_file_id={fec_file_id}')\
        .format(fec_file_id=Literal(fec_file_id))
    return query


def amendment_chain_ids(fec_file_id: str) -> SQL:
    query = SQL('SELECT amendment_id FROM fec.filing_amendment_chain WHERE fec_file_id={}')\
        .format(Literal(int(fec_file_id)))
    return query


def insert_amendment_chain(fec_file_id: str, links: List[Tuple[int, int]]) -> SQL:
    """multi-row insert of (amendment_id, amendment_number) links for one filing"""
    row = SQL('({}, {}, {}, {})')
    rows = [row.format(Literal(str(uuid.uuid4())), Literal(int(fec_file_id)), Literal(int(amendment_id)), Literal(int(amendment_number)))
            for amendment_id, amendment_number in links]
    query = SQL('INSERT INTO fec.filing_amendment_chain(filing_amendment_chain_id, fec_file_id, amendment_id, amendment_number) VALUES ') + SQL(', ').join(rows)
    return query


# BUSYNESS LOGIC

def get_filings(filters: Dict[str, str]) -> Dict[str, Any]:
    """pulls filings from openfec api"""

    path = '/filings/'
    reports = []
    openFec = OpenFec(API_KEY)
    for report in  openFec.get_route_paginator(path, filters):
        results = report['results']
        if results:
            reports.append(results)

    return reports


def get_totals(committee_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """ """

    totals_path = '/committee/' + committee_id + '/totals/'
    totals = []
    openFec = OpenFec(API_KEY)
    for report in openFec.get_route_paginator(totals_path, filters):
        results = report['results']
        if results:
            totals.append(results)

    return totals

def upsert_amendment_chain(db: Database, filing_id: str, amendment_chain: List[str]) -> bool:
    """upserts amendment chain linker table: one SELECT for what exists, one INSERT for what is missing"""

    existing = {row[0] for row in (db.query(amendment_chain_ids(filing_id)) or [])}
    links = [(int(amendment_id), amendment_number)
             for amendment_number, amendment_id in enumerate(amendment_chain)
             if int(amendment_id) not in existing]

    if not links:
        return True

    logger.debug(f'adding {len(links)} amendment links to filing {filing_id}')
    return db.try_query(insert_amendment_chain(filing_id, links))


def upsert_filing(filing: JSONType) -> bool:
    """upserts single filing record"""

    fec_file_id = filing['fec_file_id']

    if not fec_file_id or fec_file_id == 'None':
        logger.warning(f'fec_file_id missing, filing: {filing}')
        return False

    fec_file_id = fec_file_id.replace('FEC-', '')
    filing['fec_file_id'] = fec_file_id
    filing = condense_dimension(filing, 'additional_bank_names')

    amendment_chain = filing.pop('amendment_chain')

    with Database() as db:
        if amendment_chain:
            upsert_amendment_chain(db, fec_file_id, amendment_chain)

        if db.record_exists(fec_file_exists(fec_file_id)):
            logger.warning(f'Financial Summary with fec_file_id {fec_file_id} already exists')
            return True

        return db.sql_insert('filings', filing)


def upsert_committee_total(commitee_total: JSONType) -> bool:
    """upserts single commitee total given as dict/json"""

    pk1 = commitee_total['committee_id']
    pk2 = commitee_total['cycle']

    with Database() as db:
        if db.record_exists(committee_total_exists(pk1, pk2)):
            return db.sql_update('committee_totals', commitee_total, ['committee_id', 'cycle'])

        return db.sql_insert('committee_totals', commitee_total)


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html"""

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
        failed = [f for f in filings_flat if not upsert_filing(f)]
        if failed:
            logger.error(f'UPSERT_FAILED fec.filings {len(failed)}/{len(filings_flat)} '
                         f'committee_id={committee_id}')

        # handle fec.committee_totals
        # totals is list of lists, flatten it
        totals_flat = [item for sublist in totals for item in sublist]
        failed = [t for t in totals_flat if not upsert_committee_total(t)]
        if failed:
            logger.error(f'UPSERT_FAILED fec.committee_totals {len(failed)}/{len(totals_flat)} '
                         f'committee_id={committee_id}')
