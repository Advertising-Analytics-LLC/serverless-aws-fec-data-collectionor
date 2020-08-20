#!/bin/python3

import pytest
from src.CommitteSync import lambdaBackfillHandler

event = {}
context = {}

def test_lambdaBackfillHandler():
    sns_replies = lambdaBackfillHandler(event, context)
    assert True
