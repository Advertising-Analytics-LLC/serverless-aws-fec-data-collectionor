#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import psycopg2
import sys
from psycopg2 import sql, ProgrammingError
from src import JSONType, logger, schema
from src.secrets import get_param_value_by_name
from typing import List, Any


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
            value = self.curr.fetchall()
        except ProgrammingError as err:
            logger.debug(f'Query had no results, message: {err}')
            return None

        return value

    def query(self, query: sql.SQL) -> Any:
        """exec and commit a single query

        Args:
            query (sql.SQL): SQL query

        Returns:
            Any: the result of fetchall
        """
        return_value = self._query(query)
        return return_value

    def try_query(self, query: sql.SQL) -> bool:
        """query in a try block. returns bool representing success

        Args:
            query (sql.SQL): SQL query

        Returns:
            bool: query success
        """
        try:
            self._query(query)
            self.commit()
            return True
        except Exception as e:
            logger.error(sys.exc_info()[0])
            logger.error(e)
            self.rollback()
            return False

    def copy(self, sql, data_file):
        self.curr.copy_expert(sql, data_file)
        self.commit()

    def copy_from(self, sql, data_file, sep=','):
        self.curr.copy_from(data_file, sql, sep=sep)
        self.commit()

    def commit(self):
        """commits transaction
        """
        self.conn.commit()

    def rollback(self):
        """rolls back transaction
        """
        self.conn.rollback()

    def record_exists(self, query: sql.SQL) -> bool:
        """takes a select query and queries for existing records

        Args:
            query (sql.SQL): SELECT query to establish existance

        Returns:
            bool: True if exists else False
        """
        value = self._query(query)
        if value:
            logger.debug(f'Record exists for {query.as_string(self.curr)}')
            return True
        return False
