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
import uuid
import re
import time
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from src import JSONType, logger, serialize_dates
from src.database import Database
from src.sqs import parse_message


FILING_TYPE = os.environ['FILING_TYPE']
REDSHIFT_COPY_ROLE = os.environ['REDSHIFT_COPY_ROLE']

dynamodb = boto3.resource('dynamodb')
errored_fec_files_table = dynamodb.Table('errored-fec-files')

filing_table_mapping = {
    'SB': 'filings_schedule_b',
    'SE': 'filings_schedule_e',
    'F1S': 'form_1_supplemental'
}


class TransactionIdMissingException(Exception):
    """ transaction ID is misling
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


def parse_event_record(eventrecord) -> (dict, int):
    message_parsed = parse_message(eventrecord)
    filing_id = message_parsed['filing_id'].replace('FEC-', '')

    if not filing_id or filing_id == 'None':
        raise TransactionIdMissingException(
            f'Missing filing ID for filing record {message_parsed}')

    filing_id = int(filing_id)
    return message_parsed, filing_id


def create_dynamo_table(table_name_prefix):
    """ creates dynamodb table, waits for existance, returns table """
    datetime_now_string = datetime.isoformat(
        datetime.now(timezone.utc))[:-6].replace(':', '')
    table_name = f'{table_name_prefix}-{datetime_now_string}'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'fec_file_id', 'KeyType': 'HASH'},
            {'AttributeName': 'random_hash', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[
            {'AttributeName': 'fec_file_id', 'AttributeType': 'S'},
            {'AttributeName': 'random_hash', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST')

    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    return table


def iter_fec_filing(filing_id: int, insert_values: list, fec_file_ids: set):
    """ requests filing and MUTATES insert_values & fec_file_ids!!! """

    try:
        for fec_item in fecfile.iter_http(filing_id, options={'filter_itemizations': [FILING_TYPE]}):

            if fec_item.data_type != 'itemization':
                continue

            fec_file_ids.add(filing_id)
            data_dict = fec_item.data
            data_dict['fec_file_id'] = filing_id
            insert_values.append(data_dict)

    except fecfile.FilingUnavailableError as e:
        logger.error(e)
        errored_fec_files_table.put_item(
            Item={'fec_file_id': filing_id,
                  'error': str(e)})


def lambdaHandler(event: dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
        takes events that have fec file IDs, gets the filing from docquery and writes to the DB

    Args:
        event (dict): for event types see https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        bool: success
    """

    logger.debug(f'running {__file__}')
    logger.debug(json.dumps(event))

    messages = event['Records']

    insert_values = []
    fec_file_ids = set()
    database_table = filing_table_mapping[FILING_TYPE]

    for message in messages:

        try:
            message_parsed, filing_id = parse_event_record(message)
        except TransactionIdMissingException as te:
            logger.warning(te)
            continue

        iter_fec_filing(filing_id, insert_values, fec_file_ids)

    # If there was no applicable data return
    if len(insert_values) == 0:
        logger.info('No relevent FEC items. Exiting.')
        return True
    else:
        logger.info(f'Found fec_file_ids: {",".join(map(str, fec_file_ids))}')

    logger.debug(
        f'Number itemizations: {len(insert_values)}, Number FEC Filings: {len(fec_file_ids)}')

    fec_item_table = create_dynamo_table(database_table)

    # write to dynamo
    with fec_item_table.batch_writer() as writer:
        for val in insert_values:
            itm = {k: str(serialize_dates(v)).strip()
                   for k, v in val.items() if v}
            itm['random_hash'] = str(uuid.uuid4())
            logger.debug(itm)
            writer.put_item(Item=itm)

    # delete old records and copy new ones to DB
    with Database() as db:
        try:
            rows_deleted = db.query_rowcount(
                sql.SQL(f'DELETE FROM fec.{database_table} WHERE fec_file_id IN ' + '({})'
                        .format(', '.join([f'\'{str(val)}\'' for val in fec_file_ids]))))

            db.query(
                f'COPY fec.{database_table} FROM \'dynamodb://{fec_item_table.table_name}\' IAM_ROLE \'{REDSHIFT_COPY_ROLE}\' readratio 100;')

            copy_notice_msg = db.conn.notices[0]
            copy_rowcount = re.search(
                r'[,]{1}\s([0-9]*).*', copy_notice_msg).group(1)
            logger.debug(copy_notice_msg)

            if rows_deleted > int(copy_rowcount):
                logger.warning(
                    f'Expected # rows: {len(insert_values)}, # copied: {copy_rowcount}, # deleted: {rows_deleted}, fec_file_ids: {",".join(map(str, fec_file_ids))}')

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

        finally:
            fec_item_table.delete()

    return True
