#!/bin/env python3
"""
CommitteeLoader lambda:
- subscribes to topic,
- read committee IDs from queue,
- gets data from the /committees/COMMITTEE_ID API
- writes data to redshift
"""

import boto3
import json
import os
from datetime import datetime, timedelta
from time import time
from typing import List, Dict, Any
from src import logger, JSONType, schema, serialize_dates
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sqs import delete_message_from_sqs, parse_message


# SSM VARS
API_KEY = get_param_value_by_name(os.environ['API_KEY'])

def get_committee_data(committee_id: str) -> JSONType:
    """Pulls the committee data from the openFEC API
        https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__

    Args:
        committee_id (str): ID of committee

    Returns:
        json: committee data
    """

    results_json = []
    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_committee_by_id_paginator(committee_id)

    for response in response_generator:
        results_json += response['results']

    return results_json


def upsert_committeecandidate(committee_id: str, candidate_id:str) -> bool:
    """upsert single record to committee-candidate linking table

    Args:
        committee_id (str): ID of committee
        candidate_id (str): ID of candidate they endorse

    Returns:
        bool: success
    """

    record_exists_query = schema.get_committee_candidate_by_id(committee_id, candidate_id)

    with Database() as db:

        if db.record_exists(record_exists_query):
            return

        query = schema.get_committee_candidate_insert_statement(committee_id, candidate_id)

        success = db.try_query(query)
        return success


def transform_committee_detail(committee_detail: JSONType) -> JSONType:
    """handles transformation of CommitteeDetail object:
        - date this update - the database converts 'now' to a timestamp
        - rename name -> committee_name
        - convert cycles list seperated by ~

    Args:
        committee_detail (JSONType): CommitteeDetail object
    """

    committee_detail['last_updated'] = "'now'"
    committee_detail['committee_name'] = committee_detail.pop('name')
    committee_detail['cycles'] = '~'.join(str(cycle) for cycle in committee_detail['cycles'])
    return committee_detail


def upsert_committee_data(committee_data: JSONType) -> bool:
    """opens DB contextmanager and upserts committee data

    Args:
        committee_data (JSONType): CommitteeDetail object from OpenFEC API

    Returns:
        bool: success
    """

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



def committeLoader(event: dict, context: object) -> bool:
    """Gets committee IDs from SQS, pulls data from OpenFEC API, and pushes to RedShift
        and loops like that for ten minutes
    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json:
    """

    logger.info(f'running {__file__}')
    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:

        message_parsed = parse_message(message)
        committee_id = message_parsed

        committee_data = get_committee_data(committee_id)

        if not committee_data:
            logger.error(f'Committee {committee_id} not found! exiting.')
            return False

        success = upsert_committee_data(committee_data[0])

        if success:
            delete_message_from_sqs(message)

    return True
