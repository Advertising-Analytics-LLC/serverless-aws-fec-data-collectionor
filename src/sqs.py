#!/bin/env python3
"""
sqs:
- helper to work with sqs
"""

import boto3
import os
import json
from src import logger
from time import time
from typing import Any, Dict


sqs = boto3.resource('sqs')
SQS_QUEUE_NAME = os.environ['SQS_QUEUE_NAME']
logger.debug(f'using queue: {SQS_QUEUE_NAME}')
# SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', '')
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

def pull_message_from_sqs() -> Dict[str, Any]:
    """pulls a committee id from SQS
    see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message

    Returns:
        Any: SQS Message object
    """

    start_time = time()
    time_to_end = start_time + 10
    while time() < time_to_end:
        message = queue.receive_messages(MaxNumberOfMessages=1)
        if message:
            return message[0]
    logger.info('No messages received, exiting')
    return {}
