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
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from src import JSONType, logger, serialize_dates
from src.database import Database
from src.sqs import parse_message


FILING_TYPE = os.environ['FILING_TYPE']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
REDSHIFT_COPY_ROLE = os.environ['REDSHIFT_COPY_ROLE']

session = boto3.Session()
s3 = session.client('s3')

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
        raise Exception(f'Missing filing ID for filing record {message_parsed}')

    logger.debug(f'filing_id:{filing_id}:{id(filing_id)}')
    filing_id = int(filing_id)
    return message_parsed, filing_id

def get_fec_items():
    pass

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
    fec_file_ids = []
    temp_filename = f'{uuid.uuid4()}.json'
    temp_filedir = '/tmp/'
    temp_filepath = temp_filedir + temp_filename
    map(os.remove, os.listdir(temp_filedir))
    database_table = filing_table_mapping[FILING_TYPE]

    for message in messages:

        message_parsed, filing_id = parse_event_record(message)

        for fec_item in fecfile.iter_http(filing_id, options={'filter_itemizations': [FILING_TYPE]}):

            if fec_item.data_type != 'itemization':
                continue

            fec_file_ids.append(filing_id)
            data_dict = fec_item.data
            data_dict['fec_file_id'] = deepcopy(filing_id)
            insert_values.append(data_dict)

    logger.debug(f'Number of values to COPY {len(insert_values)}')
    # If there was no applicable data return
    if len(insert_values) == 0:
        return True

    with open(temp_filepath, 'w+') as fh:
        for val in insert_values:
            json.dump(val, fh, default=serialize_dates)
            fh.write('\n')
        s3.upload_fileobj(fh, S3_BUCKET_NAME, temp_filename)

    with Database() as db:
        db.query(
            sql.SQL(f'DELETE FROM fec.{database_table} WHERE fec_file_id IN ' + '({})'
               .format(', '.join([f'\'{str(val)}\'' for val in fec_file_ids]))))

        db.query(f'COPY fec.{database_table} FROM \'s3://{S3_BUCKET_NAME}/{temp_filename}\' IAM_ROLE \'{REDSHIFT_COPY_ROLE}\' FORMAT AS JSON \'auto\';')
        db.commit()

    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_filename)

    return True
