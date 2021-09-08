#!/bin/env python3
"""
sqs:
- helper to work with sqs
"""

import boto3
import os
import json
from src import logger, JSONType
from time import time
from typing import Any, Dict, List


sqs = boto3.resource('sqs')
SQS_QUEUE_NAME = os.environ['SQS_QUEUE_NAME']
logger.debug(f'using queue: {SQS_QUEUE_NAME}')
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


# TODO: move to CommmiteeSync.py
def push_committee_id_to_sqs(message_list: List[any]) -> object:
    """Pushes a list of SendMessageBatchRequestEntry (messages) to
        see https://github.com/boto/botocore/blob/f1f0c6d2e445d7c3a3f8f355eaf6d692bbf3cd6a/botocore/data/sqs/2012-11-05/service-2.json#L1238
    Args:
        message_list (List[SendMessageBatchRequestEntry]): [description]

    Returns:
        object: [description]
    """
    responses = []
    for msg in message_list:
        response = queue.send_message(
            MessageBody=json.dumps(msg['committee_id']))
        logger.debug(response)
        responses.append(response)
    return responses


def delete_message_from_sqs(message: JSONType) -> bool:
    """deletes a message from SQS

    Args:
        message (JSONType): the SQS Message object

    Returns:
        bool: if deleted
    """

    receipt_handle = message['receiptHandle']
    msg_id = message['messageId']

    response = queue.delete_messages(
        Entries=[{
            'Id': msg_id,
            'ReceiptHandle': receipt_handle
        }])

    if len(response['Successful']) > 0:
        return True

    return False


def parse_message(message: JSONType) -> Dict[str, str]:
    """parse string from sqs - it's kind of jsonish
        those coming from SNS -> SQS are JSON in a 'Message' object
        those coming from -> SQS are a string

    Args:
        message (JSON): almost json

    Returns:
        Dict[str, str]: python dictionary
    """

    my_body = message['body']

    try:
        json_body = json.loads(my_body)
        if type(json_body) == dict:
            body_content = json.loads(json_body['Message'].replace("'", '"'))

            return body_content

        return json_body.replace("'", '')
    except KeyError as ex:
        logger.error('KeyError parsing message')
        logger.error(message)
        raise ex
    except Exception as ex:
        logger.error(f'Error: {ex}\nSQS message: {message}')


def push_message_to_sqs(message: str) -> Dict[str, str]:
    """Sends unformatted message to SQS
        see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue.send_message

    Args:
        message (str): Message can be unformatted string, JSON, or XML (as string)

    Returns:
        Dict[str, str]: Response from SQS, of format:
            {
                'MD5OfMessageBody': 'string',
                'MD5OfMessageAttributes': 'string',
                'MD5OfMessageSystemAttributes': 'string',
                'MessageId': 'string',
                'SequenceNumber': 'string'
            }
    """

    response = queue.send_message(
        MessageBody=json.dumps(message))

    logger.debug(response)

    return response
