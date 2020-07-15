#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import logging
import psycopg2
from psycopg2 import sql, ProgrammingError
from src import schema, JSONType
from src.secrets import get_param_value_by_name
from typing import List, Any


# logging
logger = logging.getLogger(__name__)

# SSM VARS
DATABASE = get_param_value_by_name('/global/fec-schema/database')
HOSTNAME = get_param_value_by_name('/global/fec-schema/hostname')
PASSWORD = get_param_value_by_name('/global/fec-schema/password')
PORT = get_param_value_by_name('/global/fec-schema/port')
USERNAME = get_param_value_by_name('/global/fec-schema/username')

class Database:
    """redshift wrapper to handle data serialization
    """
    def __init__(self):
        """creates connection to redshift database and performs operations
            Gets connection variables from SSM
        """
        self.conn = psycopg2.connect(dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT)

    def __enter__(self):
        """for use as context manager (pythons with statement)

        Returns:
            self: returns itself
        """
        self.curr = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """for use as context manager (pythons with statement)

        Args:
            exc_type ([type]): [description]
            exc_value ([type]): [description]
            exc_traceback ([type]): [description]
        """
        self.curr.close()
        self.conn.close()

    def _query(self, query: sql.SQL) -> Any:
        """Query the database and fetch a result.
        If there are no results to fetch the ProgrammingError is caught and None is returned.

        Args:
            query (sql.SQL): psycopg2 SQL query

        Returns:
            Any: result or None
        """
        logger.debug(f'Executing query {query}')
        self.curr.execute(query)
        try:
            value = self.curr.fetchone()
        except ProgrammingError as err:
            logger.warning(err)
            return None
        return value

    def _transform_committee_detail(self, committee_detail: JSONType):
        """handles transformation of CommitteeDetail object:
            - date this update - the database converts 'now' to a timestamp
            - rename name -> committee_name
            - convert cycles list seperated by ~

        Args:
            committee_detail (JSONType): CommitteeDetail object
        """
        committee_detail['last_updated'] = "'now'"
        committee_detail['committee_name'] = committee_detail.pop('name')
        committee_detail['cycles'] = '~'.join(str(cycle) for cycle in committee_detail['cycles'])
        return committee_detail

    def committeecandidates_exists(self, committee_id: str, candidate_id: str) -> bool:
        query = schema.get_candidatecommittee_by_id(committee_id, candidate_id)
        value = self._query(query)
        if value:
            logger.debug(f'existing committeecandidate record {value}')
            return True
        return False

    def upsert_committeecandidates(self, committee_id: str, candidate_ids: List[str]):
        for candidate_id in candidate_ids:
            if self.candidatecommittee_exists(committee_id, candidate_id):
                continue
            query = schema.get_committeecandidates_insert_statement(committee_id, candidate_id)
            self._query(query)

    def committeedetail_exists(self, committee_id: str) -> bool:
        query = schema.get_committeedetail_by_id(committee_id)
        value = self._query(query)
        if value:
            logger.debug(f'existing committeedetail record {value}')
            return True
        return False

    def upsert_committeedetail(self, committee_detail: JSONType):
        committee_id = committee_detail['committee_id']
        candidate_ids = committee_detail.pop('candidate_ids')
        committeeDetail = self._transform_committee_detail(committee_detail)
        if self.committeedetail_exists(committee_id):
            query = schema.get_committeedetail_update_statement(**committeeDetail)
        else:
            query = schema.get_committeedetail_insert_statement(**committeeDetail)
        self._query(query)
        self.conn.commit()
