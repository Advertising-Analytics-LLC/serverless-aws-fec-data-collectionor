
#!/bin/env python3
"""
get_db_stats:
"""

from datetime import datetime, timedelta
from src import logger
from src.database import Database


queries = [
    'select count (*) from fec.candidate_detail;',
    'select min(first_file_date) from fec.candidate_detail;',
    'select count (*) from fec.committee_detail;',
    'select min(first_file_date) from fec.committee_detail;',
    'select count (*) from fec.filings;',
    'select min(receipt_date) from fec.filings;'
]


def lambdaHandler(event, context):
    with Database() as db:
        for query in queries:
            logger.info(query)
            logger.info(db.query(query))
