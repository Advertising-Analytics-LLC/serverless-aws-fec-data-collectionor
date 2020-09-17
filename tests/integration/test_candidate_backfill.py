#!/bin/env python3
"""
tests src/CandidateSync.py
"""

import os
import pytest


event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['SQS_QUEUE_NAME'] = 'candidate-sync-queue'
    from src.CandidateSync import lambdaBackfillHandler
    sns_replies = lambdaBackfillHandler(event, context)
    assert sns_replies
