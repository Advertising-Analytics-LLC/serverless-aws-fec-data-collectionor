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

from src.serialization import serialize_dates

def get_fec_file(url: str) -> bytes:
    logger.debug(f'GET {url}')
    headers = {'User-Agent': 'curl/7.64.1'}
    response = requests.get(url, allow_redirects=True, headers=headers)
    return response.text

# def parse_fec_file(fec_file: bytes) -> str:
#     newline = r'\n'
#     seperator = r'\x1c'

def lambdaHandler(event:dict, context: object) -> bool:
    """see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

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
        fec_file_dict = fecfile.from_http(filing_id)
        schedule_b_dict = fec_file_dict['itemizations']['Schedule B']

        # delete_message_from_sqs(message)

    return True
