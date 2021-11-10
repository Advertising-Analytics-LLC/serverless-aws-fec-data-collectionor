#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import psycopg2
import sys
from collections import OrderedDict
from psycopg2 import sql, ProgrammingError
from psycopg2.sql import Literal
from src import logger
from src.secrets import get_param_value_by_name
from typing import Any, Dict, List, Union


DATABASE = get_param_value_by_name('/global/fec-schema/database')
HOSTNAME = get_param_value_by_name('/global/fec-schema/hostname')
PASSWORD = get_param_value_by_name('/global/fec-schema/password')
PORT = get_param_value_by_name('/global/fec-schema/port')
USERNAME = get_param_value_by_name('/global/fec-schema/username')



##########################################
# helper funcs
##########################################

def parse_value(value: Union[str, int]) -> Union[str, int]:
    """parses values so that sql can put them into redshift"""

    if value is None:
        return ''

    return str(value)


def filter_dict_by_keys(unfiltered_dict: Dict[str, str], keys: List[str]):
    """takes a dictionary and a list of sets containing keys (because that is how redshift returns them)
    and returns a dictionary with only the keys given by the list"""

    keys_list = [ key[0] for key in keys ]
    filtered_dict = { str(key): unfiltered_dict[str(key)] for key in keys_list}

    return filtered_dict

def get_insert_query(database_table: str, values_dict: dict) -> psycopg2.sql:
    """ returns an insert query given a DB table and a dictionary of col:vals """
    values = OrderedDict(sorted(values_dict.items()))

    query_string = f'INSERT INTO {database_table} ('\
        + ', '.join([f'{key}' for key, val in values.items()]) + ') '\
        + 'VALUES (' + ', '.join(['{}' for key, val in values.items()]) + ')'

    query = sql.SQL(query_string)\
               .format(*[Literal(val) for key, val in values.items()])

    return query

##########################################
# main db class
##########################################

class Database:
    """redshift wrapper to handle data serialization"""

    def __init__(self):
        """creates connection to redshift"""
        self.conn = psycopg2.connect(dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT)

    def __enter__(self):
        """for use as context manager (pythons with statement)"""
        self.curr = self.conn.cursor()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """for use as context manager (pythons with statement)"""

        self.curr.close()
        self.conn.close()

    def query_rowcount(self, query):
        """ queries DB and returns the number of rows affected """
        logger.debug(f'Executing query {self.curr.mogrify(query)}')
        self.curr.execute(query)
        return self.curr.rowcount

    def query(self, query: sql.SQL) -> Any:
        """Query the database and fetch a result.
        If there are no results to fetch the ProgrammingError is caught and None is returned.

        Args:
            query (sql.SQL): psycopg2 SQL query

        Returns:
            Any: result or None
        """
        logger.debug(f'Executing query {self.curr.mogrify(query)}')
        self.curr.execute(query)
        logger.debug(f'Query message: {self.conn.notices}')
        logger.debug(f'Rows Affected: {self.curr.rowcount}')
        try:
            value = self.curr.fetchall()
        except ProgrammingError as err:
            logger.debug(f'Query had no results, message: {err}')
            return None

        return value

    def try_query(self, query: sql.SQL) -> bool:
        """query in a try block. returns bool representing success"""
        try:
            self.query(query)
            self.commit()
            return True
        except Exception as e:
            logger.error(sys.exc_info()[0])
            logger.error(e)
            self.rollback()
            return False

    def commit(self):
        """commits transaction"""
        self.conn.commit()

    def rollback(self):
        """rolls back transaction"""
        self.conn.rollback()

    def record_exists(self, query: sql.SQL) -> bool:
        """takes a select query and queries for existing records

        Args:
            query (sql.SQL): SELECT query to establish existance

        Returns:
            bool: True if exists else False
        """
        value = self.query(query)
        if value:
            logger.debug(f'Record exists for {self.curr.mogrify(query)}')
            return True
        return False

    ##########################################
    # sql funcs
    ##########################################



    def get_ordered_column_names_query(self, table):
        '''takes the name of a table in fmw and returns a query for all the columns'''

        query_string = f'''select column_name
    from information_schema.columns
    where table_name = '{table}'
    order by ordinal_position;'''

        query = sql.SQL(query_string)

        return query


    def get_sql_from_string(self, query_string):
        """returns a sql from string"""

        query = sql.SQL(query_string)

        return query


    def get_sql_update(self, table, values: Dict[str, str], pk_col_name):
        """returns a generic update statement"""

        ordered_columns = self.query(self.get_ordered_column_names_query(table))
        values = filter_dict_by_keys(values, ordered_columns)

        primary_key = values.pop(pk_col_name)

        query_string = f'UPDATE fec.{table} SET ' \
            + ', '.join([f' {key}={{}}' for key, val in values.items()])\
            + f' WHERE {pk_col_name}={{}}'

        query = sql.SQL(query_string)\
            .format(*[Literal(val) for key, val in values.items()], Literal(primary_key))

        return query


    def get_sql_insert(self, table, values):
        '''returns a generic insert statement'''

        ordered_columns = self.query(self.get_ordered_column_names_query(table))
        values = filter_dict_by_keys(values, ordered_columns)

        query_string = f'INSERT INTO fec.{table} ('\
            + ', '.join([f'{key}' for key, val in values.items()])\
            + ') '\
            + 'VALUES ('\
            + ', '.join(['{}' for key, val in values.items()])\
            + ')'

        def truncate(val):
            if isinstance(val, str):
                if len(val) >= 255:
                    logger.warning(f'value longer than limit:\n{val}')
                    return val[:255]
                return val

        query = sql.SQL(query_string)\
            .format(*[Literal(truncate(val)) for key, val in values.items()])

        return query
