
import boto3
import os
from src import  logger
from typing import Dict


RSS_SNS_TOPIC_ARN = os.getenv('RSS_SNS_TOPIC_ARN')
client = boto3.client('sns')


def send_message_to_sns(msg: str) -> Dict[str, str]:
    """sends a single message to sns

    Args:
        msg (str): message
    """

    logger.debug(f'sending {msg} to sns')

    sns_response = client.publish(
        TopicArn=RSS_SNS_TOPIC_ARN,
        Message=str(msg))

    return sns_response
