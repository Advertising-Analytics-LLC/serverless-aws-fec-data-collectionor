#!/bin/env python3


from datetime import datetime, timedelta
from src.database import Database


def get_previous_day(date: datetime) -> str:
    """date of previous day"""

    date_format_str = '%Y-%m-%d'
    if type(date) == str:
        date = datetime.strptime(date, date_format_str)
    days_to_subtract = 1
    datetwo = date - timedelta(days=days_to_subtract)
    return datetwo.strftime(date_format_str)


def get_next_day(date: datetime) -> str:
    """date of previous day"""

    date_format_str = '%Y-%m-%d'
    if type(date) == str:
        date = datetime.strptime(date, date_format_str)
    days_to_subtract = 1
    datetwo = date + timedelta(days=days_to_subtract)

    return datetwo.strftime(date_format_str)


def filings_sync_backfill_date(date_column='fec_file_date') -> str:
    """gets date of last filing from db"""

    query = f'select max({date_column}) from fec.backfill;'
    with Database() as db:
        query_result = db.query(query)
        last_date = query_result[0][0]
    if not last_date:
        raise Exception('No dates left in backfill table. Exiting.')
    return last_date


def filings_backfill_success(success_date: str, date_column='fec_file_date'):
    """delete that date from DB"""

    query = f'delete from fec.backfill where {date_column} = \'{success_date}\''
    with Database() as db:
        db.query(query)
        db.commit()
