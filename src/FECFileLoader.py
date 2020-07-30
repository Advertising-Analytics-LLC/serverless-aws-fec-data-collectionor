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
FILING_TYPE = os.environ['FILING_TYPE']

def upsert_schedule_b_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """upserts a single schedule B filing

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


def upsert_schedule_e_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """upserts a single schedule E filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if upsert succeeded
    """

    pk = filing['transaction_id_number']
    exists_query = schema.schedule_e_exists(pk)
    with Database() as db:
        record_exists = db.record_exists(exists_query)
        if record_exists:
            # query = schema.schedule_e_update(fec_file_id, filing)
            logger.debug('exists')
        else:
            query = schema.schedule_e_insert(fec_file_id, filing)

        return db.try_query(query)


def upsert_f1_supplemental(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """upserts a single filing of Form 1 Supplemental Data

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if upsert succeeded
    """

    pk1 = filing['affiliated_committee_id_number']
    pk2 = filing['filer_committee_id_number']

    exists_query = schema.f1_supplemental_exists(fec_file_id, filing)

    with Database() as db:
        record_exists = db.record_exists(exists_query)

        if record_exists:

            return True

        else:
            query = schema.f1_supplemental_insert(fec_file_id, filing)

        return db.try_query(query)



def upsert_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """upserts a single filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if upsert succeeded
    """

    form_type = filing['form_type']

    # Schedule B Filings
    if form_type.startswith('SB'):

        return upsert_schedule_b_filing(fec_file_id, filing)

    # Schedule E Filings
    elif form_type.startswith('SE'):

        return upsert_schedule_e_filing(fec_file_id, filing)

    # Form 1 Supplemental Data Filings
    elif form_type.startswith('F1S'):

        return upsert_f1_supplemental(fec_file_id, filing)

    else:
        logger.error(f'Filing of form_type {form_type} does not match those available')

        return False


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

        for fec_item in fecfile.iter_http(filing_id,
                                options={'filter_itemizations': [FILING_TYPE]}):

            if fec_item.data_type == 'itemization':
                upsert_filing(filing_id, fec_item.data)

        delete_message_from_sqs(message)

    return True
