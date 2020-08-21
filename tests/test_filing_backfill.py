

import os
import pytest
from src.FilingSync import lambdaBackfillHandler

event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['RSS_SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-11BQMDIOV8CJ1'
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
