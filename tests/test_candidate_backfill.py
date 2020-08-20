

import pytest
from src.CandidateSync import lambdaBackfillHandler

event = {}
context = {}

def test_lambdaBackfillHandler():
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
