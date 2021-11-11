#!/bin/env python3


import json
import os
from src import logger, condense_dimension
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.FinancialSummaryLoader import upsert_filing


API_KEY = get_param_value_by_name(os.environ['API_KEY'])


def handle_committee_pagination(pagination):
    '''paginates over committees, inserting them and their candidates into the db'''

    table_name = 'committee_candidate'
    for committee_datum in pagination['results']:
        committee_id = committee_datum['committee_id']
        candidate_ids = committee_datum.pop('candidate_ids')

        for candidate_id in candidate_ids:
            with Database() as db:

                record_exists_query = db.get_sql_query(f'SELECT * FROM fec.{table_name} WHERE committee_id = \'{committee_id}\' AND candidate_id = \'{candidate_id}\'')
                if db.record_exists(record_exists_query):
                    continue

                db.sql_insert(table_name, [candidate_id, committee_id])

        committee_datum['last_updated'] = "'now'"
        # rename name -> committee_name
        committee_datum['committee_name'] = committee_datum.pop('name')
        # convert cycles list seperated by ~
        committee_datum = condense_dimension(committee_datum, 'cycles')

        table_name = 'committee_detail'
        table_pk_name = 'committee_id'

        with Database() as db:

            committee_exists_query = db.get_sql_query(f'SELECT * FROM fec.{table_name} WHERE committee_id = \'{committee_id}\'')
            if db.record_exists(committee_exists_query):
                db.sql_update(table_name, committee_datum, table_pk_name)
            else:
                db.sql_insert(table_name, committee_datum)


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
