#!/bin/env python3
"""
tests src/backfill.py
"""

import datetime
import pytest
import re
from src import backfill
from unittest.mock import MagicMock, patch
from unittest import TestCase


def test_get_previous_day():
    dateone = '2020-08-07'
    datetwo = '2020-08-06'
    assert datetwo == backfill.get_previous_day(dateone)


def test_get_nextg_day():
    dateone = '2020-08-07'
    datetwo = '2020-08-06'
    assert dateone == backfill.get_next_day(datetwo)


def test_candidate_sync_backfill_date():
    date = backfill.candidate_sync_backfill_date()
    assert re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date)


def test_committee_sync_backfill_date():
    date = backfill.committee_sync_backfill_date()
    assert re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date)


def test_filing_sync_backfill_date():
    date = backfill.filings_sync_backfill_date()
    assert type(date) == datetime.date
