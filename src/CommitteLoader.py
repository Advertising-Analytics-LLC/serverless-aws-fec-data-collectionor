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
from src import logger, schema, condense_dimension
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.FinancialSummaryLoader import upsert_filing


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])


def committeLoader(event, context):
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift"""

    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:

        openFec = OpenFec(API_KEY)
        committee_id = message['body']

        route = f'/committee/{committee_id}/'
        committee_paginator = openFec.get_route_paginator(route)
        for pagination in committee_paginator:
            for committee_datum in pagination['results']:
                committee_id = committee_datum['committee_id']
                candidate_ids = committee_datum.pop('candidate_ids')

                for candidate_id in candidate_ids:
                    with Database() as db:

                        record_exists_query = schema.get_committee_candidate_by_id(committee_id, candidate_id)
                        if db.record_exists(record_exists_query):
                            continue

                        query = schema.get_committee_candidate_insert_statement(committee_id, candidate_id)
                        db.try_query(query)

                committee_datum['last_updated'] = "'now'"
                # rename name -> committee_name
                committee_datum['committee_name'] = committee_datum.pop('name')
                # convert cycles list seperated by ~
                committee_datum = condense_dimension(committee_datum, 'cycles')

                committee_exists_query = schema.get_committee_detail_by_id(committee_id)

                with Database() as db:
                    table_name = 'committee_detail'
                    table_pk_name = 'committee_id'
                    committee_detail_column_names = db.query(schema.get_ordered_column_names(table_name))
                    print(f'colum nnames: {committee_detail_column_names}')

                    if db.record_exists(committee_exists_query):
                        query = schema.get_sql_update(table_name, committee_detail_column_names, committee_datum, table_pk_name)
                    else:
                        query = schema.get_sql_insert(table_name, committee_detail_column_names, committee_datum)

                    db.try_query(query)

        route = f'/committee/{committee_id}/filings/?form_category=STATEMENT'
        committee_paginator = openFec.get_route_paginator(route)
        for pagination in committee_paginator:
            for filing in pagination['results']:
                upsert_filing(filing)
