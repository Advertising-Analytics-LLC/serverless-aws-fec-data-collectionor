
#!/bin/env python3
"""
get_db_stats:
    quick and dirty database stats
    created to monitor the progress of our data-loading
    sends stats to stdout at level INFO
"""

from datetime import datetime, timedelta
from psycopg2 import sql
from src import logger
from src.database import Database
from typing import List


#
# queries correspond to columns in table fec.loading_stats
queries = [
    'select count(*) from fec.candidate_detail;',
    'select count(DISTINCT candidate_id) from fec.candidate_detail;',
    'select count(*) from fec.committee_detail;',
    'select count(DISTINCT committee_id) from fec.committee_detail;',
    'select count(*) from fec.filings;',
    'select count(DISTINCT fec_file_id) from fec.filings;',
    'select count(*) from fec.committee_totals;',
    'select count(*) from (select DISTINCT cycle, committee_id from fec.committee_totals);',
    'select count(*) from fec.filing_amendment_chain;',
    'select count(DISTINCT fec_file_id) from fec.filing_amendment_chain;',
    'select count(*) from fec.filings_schedule_b;',
    'select count(DISTINCT fec_file_id) from fec.filings_schedule_b;',
    'select count(*) from fec.filings_schedule_e;',
    'select count(DISTINCT fec_file_id) from fec.filings_schedule_e;',
    'select count(*) from fec.form_1_supplemental;'
    'select count(DISTINCT fec_file_id) from fec.form_1_supplemental;'
]

def db_stats_insert(values: List[str]) -> str:
    literal_value_holes = ', '.join([ '{}' for val in values])
    query = sql.SQL(f'INSERT INTO fec.loading_stats VALUES ({literal_value_holes})')\
                .format(*[sql.Literal(val) for val in values])
    return query


def lambdaHandler(event, context):
    """ lambda that queries db and then writes stats back """

    results = ["'now'"]

    # query db with each query
    with Database() as db:
        for query in queries:
            result = db.query(query)
            result = result[0][0]
            results.append(result)
            logger.info(f'\n{query}\t\t\t{result}')

        # write stats back to DB
        insert_command = db_stats_insert(results)
        return db.try_query(insert_command)
