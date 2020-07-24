#!/bin/env python3
"""
FECFileLoader lambda:
- read FEC files from queue,
- downloads files
- parses file
- writes data to redshift
"""

import boto3
import fecfile
import json
import os
import requests
from typing import Any, Dict, List
from src import JSONType, logger, schema
from src.database import Database
from src.sqs import delete_message_from_sqs, parse_message


# business logic

def get_fec_file(url: str) -> str:
    logger.debug(f'GET {url}')
    headers = {'User-Agent': 'curl/7.64.1'}
    response = requests.get(url, allow_redirects=True, headers=headers)
    return response.text

def upsert_schedule_b_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """upserts a single filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if upsert succeeded
    """

    pk = filing['transaction_id_number']
    exists_query = schema.schedule_b_exists(pk)
    with Database() as db:
        record_exists = db.record_exists(exists_query)
        if record_exists:
            query = schema.schedule_b_update(fec_file_id, filing)
        else:
            query = schema.schedule_b_insert(fec_file_id, filing)

        success = db.try_query(query)

    return success


def upsert_schedule_b_filings(fec_file_id: str, filings: List[Dict[str, Any]]) -> List[bool]:
    """upserts a list of schedule b filings

    Args:
        filings (List[Dict[str, Any]]): List of filings
    """

    successes = []

    for filing in filings:
        success = upsert_schedule_b_filing(fec_file_id, filing)
        successes.append(success)

    return successes


def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
        takes events that have fec file IDs, gets the filing from docquery and writes to the DB

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: Did this go well?
    """

    logger.debug(f'running {__file__}')
    logger.debug(event)

    messages = event['Records']

    for message in messages:
        message_parsed = parse_message(message)
        filing_id = message_parsed['filing_id']
        logger.debug(f'Grabbing FEC filing {filing_id}')
        # fec_file_dict = fecfile.from_http(filing_id)

        guid = message_parsed['guid']
        fec_file_str = get_fec_file(guid)
        logger.debug(f'FEC filing str {fec_file_str}')
        fec_file_dict = fecfile.loads(fec_file_str)

        logger.debug(f'Got FEC filing {fec_file_dict}')
        list_of_schedule_b_dicts = fec_file_dict['itemizations']['Schedule B']

        upsert_schedule_b_filings(filing_id, list_of_schedule_b_dicts)

        delete_message_from_sqs(message)

    return True
