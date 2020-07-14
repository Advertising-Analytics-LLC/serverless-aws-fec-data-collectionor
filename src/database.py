#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import logging
import psycopg2
from psycopg2 import sql
from src import schema
from src.secrets import get_param_value_by_name


# logging
logger = logging.getLogger(__name__)

# SSM VARS
DATABASE = get_param_value_by_name('/global/fec-schema/database')
HOSTNAME = get_param_value_by_name('/global/fec-schema/hostname')
PASSWORD = get_param_value_by_name('/global/fec-schema/password')
PORT = get_param_value_by_name('/global/fec-schema/port')
USERNAME = get_param_value_by_name('/global/fec-schema/username')

class Database:
    """redshift wrapper
    """
    def __init__(self):
        """creates connection to redshift database and performs operations
            Gets connection variables from SSM
        """
        self.conn = psycopg2.connect(dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT)
    def __enter__(self):
        self.curr = self.conn.cursor()
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.curr.close()
        self.conn.close()

    def _transform_committee_detail(self, committee_detail: any):
        committee_id = committee_detail['committee_id']
        candidate_ids = committee_detail.pop('candidate_ids')
        for candidate_id in candidate_ids:
            query = schema.get_committeecandidates_insert_statement(committee_id, candidate_id)
            self.curr.execute(query)
            ret = self.curr.fetchone()
            logger.debug(ret)

        # date this update - the database converts this to a timestamp
        committee_detail['last_updated'] = "'now'"
        # rename key
        committee_detail['committee_name'] = committee_detail.pop('name')
        # convert cycles list seperated by ~
        committee_detail['cycles'] = '~'.join(str(cycle) for cycle in committee_detail['cycles'])

    def write_committee_detail(self, committee_detail: any):
        """[summary]

        Args:
            committee_detail (JSON): [description]
        """
        # try:
        committeeDetail = self._transform_committee_detail(committee_detail)
