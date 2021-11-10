#!/bin/env python3
"""
Schema holds the database objects as we can use them in code
"""

from collections import OrderedDict
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from typing import Dict



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
