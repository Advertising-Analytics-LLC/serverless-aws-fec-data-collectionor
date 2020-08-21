#!/bin/python3

import os
import pytest


event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['SQS_QUEUE_NAME'] = 'committee-sync-queue'
    from src.CommitteSync import lambdaBackfillHandler
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
