import psycopg2
import pytest
from psycopg2 import extensions

import src.database as database
from src.database import Database


def test_consecutive_blocks_reuse_one_connection(fake_pg):
    with Database() as db:
        db.query(db.get_sql_query('SELECT 1'))
    with Database() as db:
        db.query(db.get_sql_query('SELECT 2'))

    assert len(fake_pg) == 1
    assert fake_pg[0].executed == ['SELECT 1', 'SELECT 2']
    assert fake_pg[0].closed == 0


def test_connect_uses_keepalives(fake_pg):
    with Database():
        pass
    assert fake_pg[0].kwargs['keepalives'] == 1
    assert fake_pg[0].kwargs['keepalives_idle'] <= 300


def test_exit_rolls_back_open_read_transaction(fake_pg):
    with Database() as db:
        db.query(db.get_sql_query('SELECT 1'))  # opens a transaction, never committed
    conn = fake_pg[0]
    assert conn.rollbacks == 1
    assert conn.status == extensions.STATUS_READY


def test_exit_rolls_back_on_exception(fake_pg):
    with pytest.raises(RuntimeError):
        with Database() as db:
            db.query(db.get_sql_query('SELECT 1'))
            raise RuntimeError('boom')
    assert fake_pg[0].rollbacks == 1
    assert fake_pg[0].closed == 0


def test_exit_does_not_rollback_committed_work(fake_pg):
    with Database() as db:
        assert db.try_query(db.get_sql_query('INSERT INTO t VALUES (1)')) is True
    assert fake_pg[0].commits == 1
    assert fake_pg[0].rollbacks == 0


def test_notices_cleared_on_enter(fake_pg):
    with Database() as db:
        assert db.conn.notices == []


def test_stale_idle_connection_is_reopened(fake_pg, monkeypatch):
    with Database():
        pass
    monkeypatch.setattr(database, '_last_used', database.monotonic() - database.IDLE_RECONNECT_SECONDS - 1)
    with Database():
        pass
    assert len(fake_pg) == 2
    assert fake_pg[0].closed == 1


def test_closed_connection_is_reopened(fake_pg):
    with Database():
        pass
    fake_pg[0].closed = 1
    with Database():
        pass
    assert len(fake_pg) == 2


def test_execute_reconnects_once_when_socket_dropped(fake_pg):
    with Database() as db:
        db.conn.fail_next = True  # socket dies between blocks/statements, no transaction open
        db.query(db.get_sql_query('SELECT 3'))
    assert len(fake_pg) == 2
    assert fake_pg[0].executed == []
    assert fake_pg[1].executed == ['SELECT 3']
    assert fake_pg[0].closed == 1


def test_execute_does_not_mask_error_mid_transaction(fake_pg):
    with pytest.raises(psycopg2.OperationalError):
        with Database() as db:
            db.query(db.get_sql_query('SELECT 1'))
            db.conn.fail_next = True
            db.query(db.get_sql_query('SELECT 2'))
    assert len(fake_pg) == 1
    assert fake_pg[0].rollbacks == 1


def test_column_names_cached_per_table(fake_pg):
    with Database() as db:
        db.conn.results = [[('a',), ('b',)]]
        assert db.get_ordered_column_names('t') == [('a',), ('b',)]
        assert db.get_ordered_column_names('t') == [('a',), ('b',)]
    assert sum('information_schema' in q for q in fake_pg[0].executed) == 1
