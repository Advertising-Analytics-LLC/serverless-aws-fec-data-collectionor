#!/bin/env python3

"""
end-to-end tests for the serverless functions
!!!WARNING!!! running these tests populates queues
"""

import pytest
import json
import os
import src.get_db_stats
import src.FilingSync
import src.FECFileLoader
import src.CandidateSync
import src.CommitteSync


context = {}
empty_event = {}
filing_event_file = 'tests/data/fec-transaction-loading-queue.json'
secrets_file = '.env'

filing_queue_map = {
    'SB': 'fec-transaction-loading-queue',
    'SE': 'fec-new-filing-se-queue',
    'FS1': 'fec-new-filing-supplemental-data-queue'}

with open(filing_event_file) as fh:
    filing_event = json.load(fh)

with open(secrets_file, 'r') as fh:
    secrets_file_text = fh.read()

secret_lines = secrets_file_text.split('export ')
secret_nested = map(lambda x: x.split('='), secret_lines)
secrets_map = map(lambda x, y: {x: y}, secret_nested)


def test_get_db_stats():
    results = src.get_db_stats.lambdaHandler(empty_event, context)
    assert results

def test_filing_sync_lambdaHandler(monkeypatch):

    envs = merge(secrets_map, {
        'RSS_SNS_TOPIC_ARN': 'arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K'
    })

    with monkeypatch.context() as m:
        m.setattr(os, 'environ', envs)
        sns_replies = src.FilingSync.lambdaHandler(empty_event, context)

    assert sns_replies

def test_filing_sync_lambdaBackfillHandler():
    os.environ['RSS_SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K'
    sns_replies = src.FilingSync.lambdaBackfillHandler(empty_event, context)
    assert sns_replies

def test_fecfileloader():
    for key, value in filing_queue_map.items():
        print(f'key:{key}, val: {value}')
        os.environ['FILING_TYPE'] = key
        os.environ['SQS_QUEUE_NAME'] = value
        result = src.FECFileLoader.lambdaHandler(filing_event, context)

        assert result

def test_candidate_sync():
    os.environ['SQS_QUEUE_NAME'] = 'candidate-sync-queue'
    sns_replies = src.CandidateSync.lambdaBackfillHandler(empty_event, context)
    assert sns_replies

def test_committee_backfill():
    os.environ['SQS_QUEUE_NAME'] = 'committee-sync-queue'
    sns_replies = src.CommitteSync.lambdaBackfillHandler(empty_event, context)
    assert sns_replies
