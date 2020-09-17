#!/bin/env python3
"""
tests src/CommitteSync.py
"""

import os
import pytest


event = {}
context = {}

def test_lambdaBackfillHandler():
    os.environ['SQS_QUEUE_NAME'] = 'committee-sync-queue'
    from src.CommitteSync import lambdaBackfillHandler
    sns_replies = lambdaBackfillHandler(event, context)
    assert sns_replies
