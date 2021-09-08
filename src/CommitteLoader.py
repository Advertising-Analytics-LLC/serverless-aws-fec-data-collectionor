#!/bin/env python3
"""
CommitteeLoader lambda:
- subscribes to topic,
- read committee IDs from queue,
- gets data from the /committees/COMMITTEE_ID API
- writes data to redshift
"""

import json
import os
from time import time
from src import logger, JSONType, schema, serialize_dates, condense_dimension
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import delete_message_from_sqs, parse_message
from src.FinancialSummaryLoader import upsert_filing


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
openFec = OpenFec(API_KEY)


def upsert_committeecandidate(committee_id: str, candidate_id:str) -> bool:
    """upsert single record to committee-candidate linking table"""

    record_exists_query = schema.get_committee_candidate_by_id(committee_id, candidate_id)

    with Database() as db:

        if db.record_exists(record_exists_query):
            return

        query = schema.get_committee_candidate_insert_statement(committee_id, candidate_id)

        success = db.try_query(query)
        return success


def transform_committee_detail(committee_detail: JSONType) -> JSONType:
    """handles transformation of CommitteeDetail object"""

    # date this update - the database converts 'now' to a timestamp
    committee_detail['last_updated'] = "'now'"

    # rename name -> committee_name
    committee_detail['committee_name'] = committee_detail.pop('name')

    # convert cycles list seperated by ~
    committee_detail = condense_dimension(committee_detail, 'cycles')

    return committee_detail


def upsert_committee_data(committee_data: JSONType) -> bool:
    """opens DB contextmanager and upserts committee data"""

    committee_id = committee_data['committee_id']
    candidate_ids = committee_data.pop('candidate_ids')

    for candidate_id in candidate_ids:
        upsert_committeecandidate(committee_id, candidate_id)

    committee_detail = transform_committee_detail(committee_data)

    committee_exists_query = schema.get_committee_detail_by_id(committee_id)

    with Database() as db:

        if db.record_exists(committee_exists_query):
            query = schema.get_committee_detail_update_statement(**committee_detail)
        else:
            query = schema.get_committee_detail_insert_statement(**committee_detail)

        success = db.try_query(query)
        return success



def committeLoader(event: dict, context: object):
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift"""

    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:

        message_parsed = parse_message(message)
        committee_id = message_parsed

        route = f'/committee/{committee_id}/'
        committee_data = openFec.get_route_paginator(route)
        for datum in committee_data:
            upsert_committee_data(datum)

        route = f'/committee/{committee_id}/filings/?form_category=STATEMENT'
        committee_filings = openFec.get_route_paginator(route)
        for filing in committee_filings:
            upsert_filing(filing)
