#!/bin/env python3


import json
import os
from psycopg2 import sql
from psycopg2.sql import Literal
from src import logger, condense_dimension
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.FinancialSummaryLoader import upsert_filing


API_KEY = get_param_value_by_name(os.environ['API_KEY'])


def handle_committee_pagination(pagination):
    '''paginates over committees, inserting them and their candidates into the db'''

    with Database() as db:
        for committee_datum in pagination['results']:
            committee_id = committee_datum['committee_id']
            candidate_ids = committee_datum.pop('candidate_ids')

            for candidate_id in candidate_ids:
                record_exists_query = sql.SQL('SELECT * FROM fec.committee_candidate WHERE committee_id = {} AND candidate_id = {}')\
                    .format(Literal(committee_id), Literal(candidate_id))
                if db.record_exists(record_exists_query):
                    continue

                db.sql_insert('committee_candidate', {'candidate_id': candidate_id, 'committee_id': committee_id})

            committee_datum['last_updated'] = "'now'"
            # rename name -> committee_name
            committee_datum['committee_name'] = committee_datum.pop('name')
            # convert cycles list seperated by ~
            committee_datum = condense_dimension(committee_datum, 'cycles')

            committee_exists_query = sql.SQL('SELECT * FROM fec.committee_detail WHERE committee_id = {}')\
                .format(Literal(committee_id))
            if db.record_exists(committee_exists_query):
                db.sql_update('committee_detail', committee_datum, 'committee_id')
            else:
                db.sql_insert('committee_detail', committee_datum)


def committeLoader(event, context):
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift"""

    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:

        openFec = OpenFec(API_KEY)
        committee_id = message['body']

        route = f'/committee/{committee_id}/'
        openFec.stream_paginations_to_callback(handle_committee_pagination, route)

        route = f'/committee/{committee_id}/filings/?form_category=STATEMENT'
        committee_paginator = openFec.get_route_paginator(route)
        for pagination in committee_paginator:
            for filing in pagination['results']:
                upsert_filing(filing)
