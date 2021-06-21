#!/bin/env python3
"""
CandidateLoader lambda:
"""

import boto3
import fecfile
import json
import os
import requests
from typing import Any, Dict, List
from src import JSONType, logger, schema
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import delete_message_from_sqs, parse_message
from src.FinancialSummaryLoader import upsert_filing


# business logic
API_KEY = get_param_value_by_name(os.environ['API_KEY'])
openFec = OpenFec(API_KEY)

def get_canidacy_filing(candidate_id: str):
    """ https://api.open.fec.gov/developers/#/filings/get_candidate__candidate_id__filings_ """

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
    """gets list of candidate by id

    Args:
        candidate_id (str): ID of candidate, eg

    Returns:
        json: json list containing IDs
    """

    route = f'/candidate/{candidate_id}/'
    response_generator = openFec.get_route_paginator(route)

    results_json = []
    for response in response_generator:
        results_json += response['results']

        # /candidate/#/ returns a list with one record
    if len(results_json) > 0:
        return results_json[0]
    else:
        logger.warning(f'API {route} returned zero results')
        return []

def condense_dimension(containing_dict: Dict[str, Any], column_name: str) -> Dict[str, Any]:
    """takes a dimension (list) in a dictionary and joins the elements with ~s
        WARNING: this method uses dict.pop and so has side effets

    Args:
        containing_dict (Dict[str, Any]): Dictionary containing the
        column_name (str): to join

    Returns:
        Dict[str, Any]: input dict with that list as a str
    """

    containing_dict[column_name] = '~'.join([str(item) for item in containing_dict.pop(column_name)])

    return containing_dict


def upsert_candidate(candidate_message: Dict[str, Any]) -> bool:
    """upserts a single filing"""

    # condense a few lists
    candidate_message = condense_dimension(candidate_message, 'cycles')
    candidate_message = condense_dimension(candidate_message, 'election_districts')
    candidate_message = condense_dimension(candidate_message, 'election_years')

    pk = candidate_message['candidate_id']
    exists_query = schema.candidate_exists(pk)

    with Database() as db:
        if db.record_exists(exists_query):
            query = schema.candidate_update(candidate_message)
        else:
            query = schema.candidate_insert(candidate_message)

        success = db.try_query(query)

    return success

def upsert_candidate_filing(candidate_message: Dict[str, Any]) -> bool:
    """upserts a single filing"""

    candidate_message['fec_file_id'] = candidate_message['fec_file_id'].replace('FEC-', '')
    exists_query = schema.form2_exists(candidate_message['fec_file_id'])

    with Database() as db:
        if not db.record_exists(exists_query):
            query = schema.form2_insert(candidate_message)
            return db.try_query(query)


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
        takes events that have CandidateDetail in them and write to DB

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    logger.debug(f'running {__file__}, event:')
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

    return True
