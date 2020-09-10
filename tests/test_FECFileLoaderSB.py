#!/bin/env python3
"""
tests src/FilingSync.py
"""

import json
import os
import pytest

event_file = 'tests/data/fec-transaction-loading-queue.json'
with open(event_file) as fh:
    event = json.load(fh)

context = {}

def test_lambdaHandler():
    os.environ['SQS_QUEUE_NAME'] = 'fec-transaction-loading-queue'
    os.environ['FILING_TYPE'] = 'SB'
    from src.FECFileLoader import lambdaHandler
    result = lambdaHandler(event, context)
    assert result
