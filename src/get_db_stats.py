
#!/bin/env python3
"""
get_db_stats:
    quick and dirty database stats
    created to monitor the progress of our data-loading
"""

from datetime import datetime, timedelta
from psycopg2 import sql
from src import logger
from src.database import Database
from typing import List


db_ddl = """
CREATE TABLE IF NOT EXISTS fec.loading_stats (
    query_time DATE NOT NULL,
    candidate_detail_count INT,
    candidate_detail_min_first_file DATE,
    committee_detail_count INT,
    committee_detail_min_first_file DATE,
    filings_count INT,
    filings_min_receipt_date DATE,
    committee_totals_count INT,
    filing_amendment_chain_count INT,
    filings_schedule_b_count INT,
    filings_schedule_e_count INT,
    form_1_supplemental_count INT
)
"""

queries = [
    'select count (*) from fec.candidate_detail;',
    'select min(first_file_date) from fec.candidate_detail;',
    'select count (*) from fec.committee_detail;',
    'select min(first_file_date) from fec.committee_detail;',
    'select count (*) from fec.filings;',
    'select min(receipt_date) from fec.filings;',
    'select count(*) from fec.committee_totals;',
    'select count(*) from fec.filing_amendment_chain;',
    'select count(*) from fec.filings_schedule_b;',
    'select count(*) from fec.filings_schedule_e;',
    'select count(*) from fec.form_1_supplemental;'
]

def db_stats_insert(values: List[str]) -> str:
    literal_value_holes = ', '.join([ '{}' for val in values])
    query = sql.SQL(f'INSERT INTO fec.loading_stats VALUES ({literal_value_holes})')\
                .format(*[sql.Literal(val) for val in values])
    return query


def lambdaHandler(event, context):
    """ lambda that queries db and then writes stats back """

    results = ["'now'"]

    with Database() as db:
        for query in queries:
            logger.info(query)
            result = db.query(query)
            results.append(result[0][0])
            logger.debug(result)

        insert_command = db_stats_insert(results)
        return db.try_query(insert_command)
