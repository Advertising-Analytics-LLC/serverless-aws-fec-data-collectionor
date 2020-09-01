#!/bin/env python3
"""
FECFileLoader lambda:
- read FEC files from queue,
- downloads files
- parses file
- writes data to redshift

does this for a number of different filings types
"""

import boto3
import fecfile
import json
import os
import requests
from collections import OrderedDict
from typing import Any, Dict, List
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from src import JSONType, logger
from src.database import Database
from src.sqs import delete_message_from_sqs, parse_message


FILING_TYPE = os.environ['FILING_TYPE']

#
# schedule B schema
#

def schedule_b_exists(transaction_id_number: str) -> SQL:
    """returns a query to check if a transaction id has a record

    Args:
        transaction_id_number (str): ID representing transaction

    Returns:
        SQL: select query for record
    """

    query = sql.SQL('SELECT * FROM fec.filings_schedule_b WHERE transaction_id_number={}')\
                .format(Literal(transaction_id_number))

    return query


def schedule_b_insert(fec_file_id: str, filing: Dict[str, Any]) -> SQL:
    """inserts a record into fec.filings_schedule_b

    Args:
        fec_file_id (str): filing ID
        filing (Dict[str, Any]): dictionary containing transaction data of filing

    Returns:
        SQL: SQL insert query
    """

    filing['fec_file_id'] = fec_file_id
    values = OrderedDict(sorted(filing.items()))

    query_string = 'INSERT INTO fec.filings_schedule_b ('\
        + ', '.join([f'{key}' for key, val in values.items()])\
        + ') '\
        + 'VALUES ('\
        + ', '.join(['{}' for key, val in values.items()])\
        + ')'

    query = sql.SQL(query_string)\
                .format(*[Literal(val) for key, val in values.items()])

    return query

#
# schedule E schema
#

def schedule_e_exists(transaction_id_number: str) -> SQL:
    """returns a query to check if a transaction id has a record

    Args:
        transaction_id_number (str): ID representing transaction

    Returns:
        SQL: select query for record
    """

    query = sql.SQL('SELECT * FROM fec.filings_schedule_e WHERE transaction_id_number={}')\
                .format(Literal(transaction_id_number))

    return query


def schedule_e_insert(fec_file_id: str, filing: Dict[str, Any]) -> SQL:
    """inserts a record into fec.filings_schedule_e

    Args:
        fec_file_id (str): filing ID
        filing (Dict[str, Any]): dictionary containing transaction data of filing

    Returns:
        SQL: SQL insert query
    """

    filing['fec_file_id'] = fec_file_id
    values = OrderedDict(sorted(filing.items()))

    query_string = 'INSERT INTO fec.filings_schedule_e ('\
        + ', '.join([f'{key}' for key, val in values.items()])\
        + ') '\
        + 'VALUES ('\
        + ', '.join(['{}' for key, val in values.items()])\
        + ')'

    query = sql.SQL(query_string)\
                .format(*[Literal(val) for key, val in values.items()])

    return query

#
# Form 1 Supplemental schema
#

def f1_supplemental_exists(fec_file_id: str, filing: Dict[str, Any]) -> SQL:
    """checks for existining supplemental data

    Args:
        fec_file_id (str): Filing ID
        filing (Dict[str, Any]): dictionary containing transaction data of filing

    Returns:
        SQL: select query
    """

    filing['fec_file_id'] = fec_file_id
    values = OrderedDict(sorted(filing.items()))

    query_string = 'SELECT * FROM fec.form_1_supplemental WHERE ' \
        + ' AND '.join([f' {key}={{}}' for key, val in values.items()])

    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()])

    return query


def f1_supplemental_insert(fec_file_id: str, filing: Dict[str, Any]) -> SQL:
    """inserts a record into fec.form_1_supplemental

    Args:
        fec_file_id (str): filing ID
        filing (Dict[str, Any]): dictionary containing transaction data of filing

    Returns:
        SQL: SQL insert query
    """

    filing['fec_file_id'] = fec_file_id
    values = OrderedDict(sorted(filing.items()))

    query_string = 'INSERT INTO fec.form_1_supplemental ('\
        + ', '.join([f'{key}' for key, val in values.items()])\
        + ') '\
        + 'VALUES ('\
        + ', '.join(['{}' for key, val in values.items()])\
        + ')'

    query = sql.SQL(query_string)\
                .format(*[Literal(val) for key, val in values.items()])

    return query

#
# business logic
#

def insert_schedule_b_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """inserts a single schedule B filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if in database
    """

    pk = filing['transaction_id_number']
    exists_query = schedule_b_exists(pk)
    with Database() as db:
        record_exists = db.record_exists(exists_query)
        if record_exists:
            logger.debug(f'Record {pk} exists')

            return True

        else:
            query = schedule_b_insert(fec_file_id, filing)

            return db.try_query(query)


def insert_schedule_e_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """inserts a single schedule E filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if in database
    """

    pk = filing['transaction_id_number']
    exists_query = schedule_e_exists(pk)
    with Database() as db:
        record_exists = db.record_exists(exists_query)
        if record_exists:
            logger.debug(f'Record {pk} exists')


            return True

        else:
            query = schedule_e_insert(fec_file_id, filing)

            return db.try_query(query)


def insert_f1_supplemental(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """inserts a single filing of Form 1 Supplemental Data

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if in database
    """

    exists_query = f1_supplemental_exists(fec_file_id, filing)
    with Database() as db:
        record_exists = db.record_exists(exists_query)
        if record_exists:

            return True

        else:
            query = f1_supplemental_insert(fec_file_id, filing)

            return db.try_query(query)



def insert_filing(fec_file_id: str, filing: Dict[str, Any]) -> bool:
    """inserts a single filing

    Args:
        fec_file_id (str): FEC filing ID
        filing (Dict[str, Any]): Filing object

    Returns:
        bool: if in database
    """

    form_type = filing['form_type']

    # Schedule B Filings
    if form_type.startswith('SB'):

        return insert_schedule_b_filing(fec_file_id, filing)


    # Schedule E Filings
    elif form_type.startswith('SE'):

        return insert_schedule_e_filing(fec_file_id, filing)

    # Form 1 Supplemental Data Filings
    elif form_type.startswith('F1S'):

        return insert_f1_supplemental(fec_file_id, filing)

    else:
        logger.error(f'Filing of form_type {form_type} does not match those available')

        return False

# def get_filing(fec_file_id: str, options: dict):
#     url = 'https://docquery.fec.gov/dcdev/posted/{n}.fec'.format(n=fec_file_id)
#     req_headers = {'User-Agent': 'Mozilla/5.0'}
#     logger.debug(f'GET {url}')
#     r = requests.get(url, headers=req_headers, stream=True)
#     logger.debug(f'status {r.status_code}')
#     for item in fecparser.iter_lines(r.iter_lines(), options=options):
#         yield item


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
    logger.debug(json.dumps(event))

    messages = event['Records']

    for message in messages:
        message_parsed = parse_message(message)
        filing_id = message_parsed['filing_id']

        # for fec_item in get_filing(filing_id,
        #                         options={'filter_itemizations': [FILING_TYPE]}):
        for fec_item in fecfile.iter_http(filing_id,
                                options={'filter_itemizations': [FILING_TYPE]}):

            if fec_item.data_type == 'itemization':
                insert_filing(filing_id, fec_item.data)

        delete_message_from_sqs(message)

    return True
