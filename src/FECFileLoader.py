#!/bin/env python3
"""
FECFileLoader lambda:
- read FEC files from queue,
- downloads files
- parses file
- writes data to redshift
"""

import boto3
import json
import os
from requests import Response
from typing import Any, Dict, List
from src import JSONType, logger, schema
from src.database import Database
from src.sqs import delete_message_from_sqs, parse_message


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
        exit(1)

        message_parsed = parse_message(message)

        delete_message_from_sqs(message)

    return True
