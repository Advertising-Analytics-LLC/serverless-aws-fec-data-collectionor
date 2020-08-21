
import os
import pytest
from src.CandidateSync import lambdaBackfillHandler

event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['SQS_QUEUE_NAME'] = 'candidate-sync-queue'
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
