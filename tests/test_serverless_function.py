#!/bin/env python3

"""
end-to-end tests for the serverless functions
!!!WARNING!!! running these tests populates queues
"""

import pytest
import json
import os
from functools import reduce
import src.get_db_stats
import src.FilingSync
import src.FECFileLoader
import src.CandidateSync
import src.CommitteSync
from src import logger


context = {}
empty_event = {}

filing_queue_map = {
    'SB': 'fec-transaction-loading-queue',
    'SE': 'fec-new-filing-se-queue',
    'FS1': 'fec-new-filing-supplemental-data-queue'}

def merge_dicts(d1, d2):
    return d1.update(d2)

def load_json(filename):
    """ helper function to load json from file """
    with open(filename) as fh:
        return json.load(fh)

def load_text(filename):
    """ helper function to load text from file """
    with open(filename) as fh:
        return fh.read()

def get_common_env_vars() -> dict:
    secrets_file = '.env'
    secrets_file_text = load_text(secrets_file).replace('export ', '')
    secret_lines = secrets_file_text.split('\n')
    secret_nested = list(map(lambda x: x.split('='), secret_lines))
    secret_map = {}
    for secret_tuple in secret_nested:
        secret_map[secret_tuple[0]] = secret_tuple[1]
    return secret_map

@pytest.fixture
def empty_event(monkeypatch) -> (dict, dict, dict):
    """ sets up for lambda that gets an empty event """
    envs = get_common_env_vars()
    for key, val in envs.items():
        monkeypatch.setenv(key, val)
    return empty_event, context

@pytest.fixture
def filing(monkeypatch):
    """ sets up for lambda that an event from the filing SNS -> SQS fannout queues """
    env_map = get_common_env_vars()
    filing_event_file = 'tests/data/fec-transaction-loading-queue.json'
    filing_event = load_json(filing_event_file)
    return filing_event, context

@pytest.fixture
def setup_candidate(monkeypatch):
    env_map = get_common_env_vars()
    candidate_event_file = ''
    candidate_event = load_json(candidate_event_file)
    pass

@pytest.fixture
def setup_committee(monkeypatch):
    env_map = get_common_env_vars()
    pass

def test_get_common_env_vars():
    envs = get_common_env_vars()
    logger.debug(envs)
    assert True

def test_get_db_stats(empty_event):
    event, context = empty_event
    results = src.get_db_stats.lambdaHandler(event, context)
    assert results

def test_filing_sync_lambdaHandler(empty_event):
    event, context = empty_event
    sns_replies = src.FilingSync.lambdaHandler(event, context)
    assert sns_replies

# def test_filing_sync_lambdaBackfillHandler():
#     os.environ['RSS_SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K'
#     sns_replies = src.FilingSync.lambdaBackfillHandler(empty_event, context)
#     assert sns_replies

# def test_fecfileloader():
#     for key, value in filing_queue_map.items():
#         print(f'key:{key}, val: {value}')
#         os.environ['FILING_TYPE'] = key
#         os.environ['SQS_QUEUE_NAME'] = value
#         result = src.FECFileLoader.lambdaHandler(filing_event, context)

#         assert result

# def test_candidate_sync():
#     os.environ['SQS_QUEUE_NAME'] = 'candidate-sync-queue'
#     sns_replies = src.CandidateSync.lambdaBackfillHandler(empty_event, context)
#     assert sns_replies

# def test_committee_backfill():
#     os.environ['SQS_QUEUE_NAME'] = 'committee-sync-queue'
#     sns_replies = src.CommitteSync.lambdaBackfillHandler(empty_event, context)
#     assert sns_replies
