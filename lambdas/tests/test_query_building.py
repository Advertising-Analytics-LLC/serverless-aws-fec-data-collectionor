"""SQL generation for the payload-driven loaders.

Regression cover for the fec.committee_totals outage: openFEC added first_f1_date
to its committee-totals response, the query builder took payload keys as column
names verbatim, and every write to the table failed from 2022 onward.
"""

import pytest

from conftest import render


COMMITTEE_TOTALS_COLUMNS = [
    ('committee_id',), ('cycle',), ('receipts',), ('disbursements',),
    ('committee_name',), ('first_file_date',), ('coverage_end_date',),
]


@pytest.fixture
def db(fake_pg):
    """a Database whose information_schema lookup returns COMMITTEE_TOTALS_COLUMNS"""
    from src.database import Database

    database = Database()
    with database as handle:
        database.conn.results.append(COMMITTEE_TOTALS_COLUMNS)
        yield handle


def payload(**overrides):
    values = {
        'committee_id': 'C00123456',
        'cycle': 2026,
        'receipts': 1234.56,
        'disbursements': 0,
        'committee_name': 'A COMMITTEE',
        'first_file_date': '2019-01-01',
        'coverage_end_date': None,
    }
    values.update(overrides)
    return values


def test_insert_drops_unknown_payload_key(db):
    """the actual outage: a field openFEC added that the table does not have"""
    query = render(db.get_sql_insert_query('committee_totals', payload(first_f1_date='2019-01-01')))

    assert 'first_f1_date' not in query
    assert 'first_file_date' in query


def test_update_drops_unknown_payload_key(db):
    query = render(db.get_sql_update_query(
        'committee_totals', payload(first_f1_date='2019-01-01'), ['committee_id', 'cycle']))

    assert 'first_f1_date' not in query
    assert 'first_file_date' in query


def test_insert_preserves_numeric_values(db):
    """non-strings must survive truncate(); NULLing them would be worse than the outage"""
    query = render(db.get_sql_insert_query('committee_totals', payload()))

    assert '1234.56' in query
    assert '2026' in query
    assert ', 0' in query or '(0' in query


def test_update_preserves_numeric_values(db):
    query = render(db.get_sql_update_query('committee_totals', payload(), ['committee_id', 'cycle']))

    assert 'receipts=1234.56' in query.replace(' ', '')
    assert 'disbursements=0' in query.replace(' ', '')


def test_none_stays_null_not_the_string_none(db):
    query = render(db.get_sql_insert_query('committee_totals', payload()))

    assert "'None'" not in query


def test_long_strings_are_truncated(db):
    long_name = 'X' * 400
    query = render(db.get_sql_insert_query('committee_totals', payload(committee_name=long_name)))

    assert 'X' * 255 in query
    assert 'X' * 256 not in query


def test_composite_primary_key_in_where_not_in_set(db):
    query = render(db.get_sql_update_query(
        'committee_totals', payload(), ['committee_id', 'cycle']))

    where = query.split('WHERE')[1]
    assert "committee_id='C00123456'" in where.replace(' ', '')
    assert 'cycle=2026' in where.replace(' ', '')

    set_clause = query.split('WHERE')[0]
    assert 'committee_id' not in set_clause
    assert 'cycle' not in set_clause


def test_single_string_primary_key_still_works(db):
    """CommitteLoader and CandidateLoader pass a bare column name"""
    query = render(db.get_sql_update_query('committee_totals', payload(), 'committee_id'))

    assert "WHERE committee_id='C00123456'" in query
    assert 'AND' not in query.split('WHERE')[1]


def test_unknown_keys_are_logged(db, caplog):
    import logging

    with caplog.at_level(logging.WARNING):
        db.get_sql_insert_query('committee_totals', payload(first_f1_date='2019-01-01'))

    assert any('first_f1_date' in record.message for record in caplog.records)
