#!/bin/env python3


import json
import os
from typing import Any, Dict
from src import condense_dimension, logger
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.FinancialSummaryLoader import upsert_filing


API_KEY = get_param_value_by_name(os.environ['API_KEY'])
openFec = OpenFec(API_KEY)


def get_canidacy_filing(candidate_id: str):
    """https://api.open.fec.gov/developers/#/filings/get_candidate__candidate_id__filings_"""

    route = f'/candidate/{candidate_id}/filings/?form_category=STATEMENT'
    response_generator = openFec.get_route_paginator(route)

    results_json = []
    for response in response_generator:
        results_json += response['results']

    if len(results_json) > 0:

        return results_json[0]

    else:
        logger.warning(f'API {route} returned zero results')

        return []


def get_candidate(candidate_id: str) -> Dict['str', Any]:
    """gets list of candidate by id"""

    route = f'/candidate/{candidate_id}/'
    response_generator = openFec.get_route_paginator(route)

    results_json = []
    for response in response_generator:
        results_json += response['results']

        # /candidate/#/ returns a list with one record
    if len(results_json) == 1:

        return results_json[0]

    elif len(results_json) > 1:
        logger.warning(f'too many candidates returned from api length: {len(results_json)}')

        return results_json[0]

    else:
        logger.warning(f'API {route} returned zero results')

        return []


def upsert_candidate(candidate_message: Dict[str, Any]) -> bool:
    """upserts a single filing"""

    # condense a few lists
    candidate_message = condense_dimension(candidate_message, 'cycles')
    candidate_message = condense_dimension(candidate_message, 'election_districts')
    candidate_message = condense_dimension(candidate_message, 'election_years')

    pk = {}
    table_name = 'candidate_detail'
    table_pk_name = 'candidate_id'

    try:
        pk = candidate_message[table_pk_name]
    except TypeError as e:
        logger.debug(candidate_message)
        raise e


    with Database() as db:
        exists_query = f'SELECT * FROM fec.{table_name} WHERE candidate_id=\'{pk}\''
        if db.record_exists(db.get_sql_query(exists_query)):
            query_result = db.sql_update(table_name, candidate_message, table_pk_name)
        else:
            query_result = db.sql_insert(table_name, candidate_message)

    return query_result


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html"""

    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:
        body = json.loads(message['body'])
        candidate_id = body['candidate_id']

        candidate_detail = get_candidate(candidate_id)
        if candidate_detail:
            upsert_candidate(candidate_detail)

        candidacy_filing = get_canidacy_filing(candidate_id)
        if candidacy_filing:
            upsert_filing(candidacy_filing)
