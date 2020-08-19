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
from src.secrets import get_param_value_by_name
from src.database import Database


def candidate_sync_backfill_date() -> str:
    last_date = candidate_sync_last_day()
    return get_previous_day(last_date)

def get_previous_day(date: str) -> str:
    """date of previous day

    Args:
        date (str): date in question date like 2020-08-07

    Returns:
        str: the previous day, ie 2020-08-06
    """

    days_to_subtract = 1
    return date - timedelta(days=days_to_subtract)

def candidate_sync_last_day() -> str:
    query = 'select max(first_file_date) from fec.candidate_detail;'
    with Database() as db:

        return db.query(query)
