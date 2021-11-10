#!/bin/env python3
"""
Schema holds the database objects as we can use them in code
"""

from collections import OrderedDict
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from typing import Dict, Union


def parse_value(value: Union[str, int]) -> Union[str, int]:
    """parses values so that sql can put them into redshift"""

    if value is None:
        return ''

    return str(value)


def filter_dict_by_keys(unfiltered_dict, keys):
    """takes a dictionary and a list of sets containing keys (because that is how redshift returns them
    and returns a dictionary with only the keys given by the list"""

    keys_list = [ key[0] for key in keys ]
    filtered_dict = { str(key): unfiltered_dict[str(key)] for key in keys_list}

    return filtered_dict


def get_ordered_column_names(table):
    '''takes the name of a table in fmw and returns a query for all the columns'''

    query_string = f'''select column_name
from information_schema.columns
where table_name = '{table}'
order by ordinal_position;'''

    query = sql.SQL(query_string)

    return query


def get_sql_update(table, ordered_columns, values, pk_col_name):
    """returns a generic update statement"""

    values = filter_dict_by_keys(values, ordered_columns)

    primary_key = values.pop(pk_col_name)

    query_string = f'UPDATE fec.{table} SET ' \
        + ', '.join([f' {key}={{}}' for key, val in values.items()])\
        + f' WHERE {pk_col_name}={{}}'

    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()], Literal(primary_key))

    return query


def get_sql_insert(table, ordered_columns, values):
    '''returns a generic insert statement'''

    values = filter_dict_by_keys(values, ordered_columns)

    query_string = f'INSERT INTO fec.{table} ('\
        + ', '.join([f'{key}' for key, val in values.items()])\
        + ') '\
        + 'VALUES ('\
        + ', '.join(['{}' for key, val in values.items()])\
        + ')'

    def truncate(val):
        if isinstance(val, str):
            return val[:255]

    query = sql.SQL(query_string)\
        .format(*[Literal(truncate(val)) for key, val in values.items()])

    return query



# committees

def get_committee_detail_by_id(committee_id: str) -> SQL:
    query = sql.SQL('SELECT * FROM fec.committee_detail WHERE committee_id = {committee_id}')\
        .format(committee_id=Literal(parse_value(committee_id)))
    return query

def get_committee_candidate_by_id(committee_id: str, candidate_id: str) -> SQL:
    query = SQL('SELECT * FROM fec.committee_candidate WHERE committee_id = {committee_id} AND candidate_id = {candidate_id}')\
        .format(committee_id=Literal(parse_value(committee_id)), candidate_id=Literal(parse_value(candidate_id)))
    return query


def get_committee_candidate_insert_statement(committee_id: str, candidate_id: str) -> SQL:
    """returns SQL query object to insert committee_candidate record"""

    query = sql.SQL('''
    INSERT INTO fec.committee_candidate(committee_id, candidate_id)
    VALUES ({committee_id}, {candidate_id})
    ''').format(committee_id=Literal(committee_id), candidate_id=Literal(candidate_id))
    return query


#
# Candidates
#


def candidate_exists(candidate_id: str) -> SQL:
    """returns a query to check if a candidate id has a record"""

    query = sql.SQL('SELECT * FROM fec.candidate_detail WHERE candidate_id={}')\
        .format(Literal(candidate_id))

    return query


def candidate_insert(candidate: Dict[str, str]) -> SQL:
    """inserts a record into fec.candidate_details"""

    values = OrderedDict(sorted(candidate.items()))

    query_string = 'INSERT INTO fec.candidate_detail ('\
        + ', '.join([f'{key}' for key, val in values.items()])\
        + ') '\
        + 'VALUES ('\
        + ', '.join(['{}' for key, val in values.items()])\
        + ')'

    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()])

    return query


def candidate_update(candidate: Dict[str, str]) -> SQL:
    """updates a record in fec.candidate_detail"""

    primary_key = candidate['candidate_id']
    values = OrderedDict(sorted(candidate.items()))

    query_string = 'UPDATE fec.candidate_detail SET ' \
        + ', '.join([f' {key}={{}}' for key, val in values.items()])\
        + ' WHERE candidate_id={}'

    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()], Literal(primary_key))

    return query
