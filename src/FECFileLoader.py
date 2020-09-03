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
import csv
import fecfile
import json
import os
import requests
import uuid
from collections import OrderedDict
from typing import Any, Dict, List
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from src import JSONType, logger, serialize_dates
from src.database import Database
from src.sqs import parse_message


FILING_TYPE = os.environ['FILING_TYPE']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
REDSHIFT_COPY_ROLE = os.environ['REDSHIFT_COPY_ROLE']


filing_table_mapping = {
    'SB': 'filings_schedule_b',
    'SE': 'filings_schedule_e',
    'F1S': 'form_1_supplemental'
}


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
    transaction_id_list = []
    temp_filename = f'{uuid.uuid4()}.json'
    database_table = filing_table_mapping[FILING_TYPE]

    for message in messages:
        message_parsed = parse_message(message)
        filing_id = message_parsed['filing_id']

        for fec_item in fecfile.iter_http(filing_id,
                                          options={'filter_itemizations': [FILING_TYPE]}):

            if fec_item.data_type != 'itemization':
                continue

            data_dict = fec_item.data
            data_dict['fec_file_id'] = filing_id
            insert_values.append(data_dict)
            transaction_id_list.append(data_dict['transaction_id_number'])

    # If there was no applicable data return
    if len(insert_values) == 0:
        return True

    with open(temp_filename, 'w+') as fh:
        for val in insert_values:
            json.dump(val, fh, default=serialize_dates)
            fh.write('\n')

    with open(temp_filename, 'rb') as fh:
        s3 = boto3.client('s3')
        s3.upload_fileobj(fh, S3_BUCKET_NAME, temp_filename)
        os.remove(temp_filename)

    with Database() as db:
        db.query(
            sql.SQL(f'DELETE FROM fec.{database_table} WHERE transaction_id_number IN'+' ({})'
                .format(', '.join([f'\'{str(val)}\'' for val in transaction_id_list]))))

        db.query(f'COPY fec.{database_table} FROM \'s3://{S3_BUCKET_NAME}/{temp_filename}\' IAM_ROLE \'{REDSHIFT_COPY_ROLE}\' FORMAT AS JSON \'auto\';')

    s3 = boto3.client('s3')
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_filename)

    return True
