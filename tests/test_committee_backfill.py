#!/bin/python3

import os
import pytest
from src.CommitteSync import lambdaBackfillHandler

event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['SQS_QUEUE_NAME'] = 'committee-sync-queue'
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
