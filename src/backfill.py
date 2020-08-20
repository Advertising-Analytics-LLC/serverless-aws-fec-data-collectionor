#!/bin/env python3
"""
Backfill:
    helper functions for backfilling data
"""

import boto3
import os
from datetime import datetime, timedelta
from typing import List, Dict
from src import logger
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.database import Database
from src.FilingSync import send_message_to_sns


def get_previous_day(date: datetime) -> str:
    """date of previous day

    Args:
        date (str): date in question date like 2020-08-07

    Returns:
        str: the previous day, ie 2020-08-06
    """

    date_format_str = '%Y-%m-%d'
    if type(date) == str:
        date = datetime.strptime(date, date_format_str)
    days_to_subtract = 1
    datetwo = date - timedelta(days=days_to_subtract)
    return datetwo.strftime(date_format_str)


def get_next_day(date: datetime) -> str:
    """date of previous day

    Args:
        date (str): date in question date like 2020-08-07

    Returns:
        str: the previous day, ie 2020-08-06
    """

    date_format_str = '%Y-%m-%d'
    if type(date) == str:
        date = datetime.strptime(date, date_format_str)
    days_to_subtract = 1
    datetwo = date + timedelta(days=days_to_subtract)
    return datetwo.strftime(date_format_str)


def candidate_sync_backfill_date() -> str:
    query = 'select min(first_file_date) from fec.candidate_detail;'
    with Database() as db:
        results = db.query(query)
        last_date = results[0][0]
    return get_previous_day(last_date)


def committee_sync_backfill_date() -> str:
    query = 'select min(last_file_date) from fec.committee_detail;'
    with Database() as db:
        last_date = db.query(query)
    return get_previous_day(last_date)
