#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import psycopg2
import sys
from psycopg2 import extensions
from time import monotonic
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


def truncate(val):
    """clips strings to what the VARCHAR(256) columns hold; non-strings pass through untouched.

    The non-string branch matters: fec.committee_totals is ~100 NUMERIC columns, and
    returning None for them would write NULL for every dollar figure."""

    if isinstance(val, str) and len(val) >= 255:
        logger.warning(f'value longer than limit:\n{val}')
        return val[:255]

    return val


def filter_dict_by_keys(unfiltered_dict: Dict[str, str], keys: List[str], table: str = ''):
    """takes a dictionary and a list of sets containing keys (because that is how redshift returns them)
    and returns a dictionary with only the keys given by the list.

    Payload keys the table does not have are dropped rather than passed through to
    the query builder: openFEC adds fields to its responses without warning, and an
    unknown column name fails the whole statement. Dropping is logged at warning
    because it means the table is now missing data the API is publishing."""

    keys_list = [ key[0] for key in keys ]
    filtered_dict = {}
    for key in keys_list:
        if key in unfiltered_dict.keys():
            filtered_dict[key] = unfiltered_dict[str(key)]
        else:
            logger.debug(f'column {key} has no value in this payload')

    unknown = sorted(set(unfiltered_dict) - set(keys_list))
    if unknown:
        logger.warning(f'dropping keys absent from {table or "table"}: {unknown}')

    return filtered_dict

##########################################
# connection reuse
##########################################

# One connection per warm Lambda container. The NAT gateway drops idle flows
# after 350s, so anything parked longer than IDLE_RECONNECT_SECONDS is
# reopened rather than trusted.
IDLE_RECONNECT_SECONDS = 300

_conn = None
_last_used = 0.0
_column_cache: Dict[str, List] = {}


def _connect():
    return psycopg2.connect(
        dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT,
        keepalives=1, keepalives_idle=60, keepalives_interval=10, keepalives_count=3,
    )


def _get_connection(force_new: bool = False):
    """returns the shared connection, reconnecting if it is closed, stale or force_new"""
    global _conn, _last_used

    stale = _conn is not None and (monotonic() - _last_used) > IDLE_RECONNECT_SECONDS
    if force_new or _conn is None or _conn.closed or stale:
        if _conn is not None and not _conn.closed:
            try:
                _conn.close()
            except Exception:  # best effort; the socket may already be gone
                pass
        logger.debug('opening redshift connection')
        _conn = _connect()

    _last_used = monotonic()
    return _conn


##########################################
# main db class
##########################################

class Database:
    """redshift wrapper to handle data serialization

    Use as a context manager. Each `with` block borrows the container-wide
    connection, gets a fresh cursor, and on exit rolls back anything left
    uncommitted so no transaction leaks into the next block. The connection
    itself stays open for the next block or invocation."""

    def __init__(self):
        """borrows the shared connection to redshift"""
        self.conn = _get_connection()

    def __enter__(self):
        """for use as context manager (pythons with statement)"""
        del self.conn.notices[:]  # FECFileLoader reads notices[0] after COPY
        self.curr = self.conn.cursor()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """for use as context manager (pythons with statement)"""
        global _last_used

        try:
            self.curr.close()
        except Exception:
            pass

        if self.conn.closed:
            return

        if exc_type is not None or self.conn.status == extensions.STATUS_IN_TRANSACTION:
            try:
                self.conn.rollback()
            except Exception as err:
                logger.warning(f'rollback on exit failed: {err}')

        _last_used = monotonic()

    def _execute(self, query):
        """executes on the shared connection; reconnects once if the socket went stale.

        Only retries when no transaction was open before this statement: earlier
        statements of a transaction die with the socket, and replaying just the
        last one would silently commit a partial transaction."""
        in_transaction = not self.conn.closed and self.conn.status == extensions.STATUS_IN_TRANSACTION
        try:
            self.curr.execute(query)
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as err:
            if in_transaction:
                raise
            logger.warning(f'redshift connection lost ({err}); reconnecting')
            self.conn = _get_connection(force_new=True)
            self.curr = self.conn.cursor()
            self.curr.execute(query)

    def query_rowcount(self, query):
        """ queries DB and returns the number of rows affected """
        logger.debug(f'Executing query {self.curr.mogrify(query)}')
        self._execute(query)
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
        self._execute(query)
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
            logger.error(f'QUERY_FAILED {sys.exc_info()[0]}')
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

        query_string = 'select column_name from information_schema.columns ' + \
                      f'where table_schema = \'fec\' and table_name = \'{table}\' ' + \
                       'order by ordinal_position;'

        query = sql.SQL(query_string)

        return query


    def get_sql_query(self, query_string):
        """returns a sql from string"""

        query = sql.SQL(query_string)

        return query


    def sql_query(self, query_string):
        '''executes arbitrary sql string'''

        query = self.get_sql_query(query_string)

        return query


    def get_ordered_column_names(self, table) -> List:
        """column names of fec.<table>, cached per container (information_schema is slow on redshift)"""

        if table not in _column_cache:
            _column_cache[table] = self.query(self.get_ordered_column_names_query(table))

        return _column_cache[table]


    def get_sql_update_query(self, table, values: Dict[str, str], pk_col_name):
        """returns a generic update statement.

        pk_col_name is a column name or a list of them, for tables keyed on more
        than one column (fec.committee_totals is keyed on committee_id + cycle)."""

        pk_col_names = [pk_col_name] if isinstance(pk_col_name, str) else list(pk_col_name)

        ordered_columns = self.get_ordered_column_names(table)
        values = filter_dict_by_keys(values, ordered_columns, table)

        primary_keys = [values.pop(name) for name in pk_col_names]

        query_string = f'UPDATE fec.{table} SET ' \
            + ', '.join([f' {key}={{}}' for key, val in values.items()])\
            + ' WHERE ' + ' AND '.join([f'{name}={{}}' for name in pk_col_names])

        query = sql.SQL(query_string)\
            .format(*[Literal(truncate(val)) for key, val in values.items()],
                    *[Literal(key) for key in primary_keys])

        return query


    def sql_update(self, table, values: Dict[str, str], pk_col_name):
        '''perform sql update'''

        query = self.get_sql_update_query(table, values, pk_col_name)
        result = self.try_query(query)

        return result


    def get_sql_insert_query(self, table, values):
        '''returns a generic insert statement'''

        ordered_columns = self.get_ordered_column_names(table)
        values = filter_dict_by_keys(values, ordered_columns, table)

        query_string = f'INSERT INTO fec.{table} ('\
            + ', '.join([f'{key}' for key, val in values.items()])\
            + ') '\
            + 'VALUES ('\
            + ', '.join(['{}' for key, val in values.items()])\
            + ')'

        query = sql.SQL(query_string)\
            .format(*[Literal(truncate(val)) for key, val in values.items()])

        return query


    def sql_insert(self, table, values: Dict[str, str]):
        '''perform sql insert'''

        query = self.get_sql_insert_query(table, values)
        result = self.try_query(query)

        return result
