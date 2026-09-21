"""Offline test harness: no AWS, no Redshift.

`src.secrets` and `src.sqs` talk to SSM/SQS at import time, so they are replaced
with stubs before anything under `src` is imported. `psycopg2.connect` is
replaced with a recording fake so `Database` can be exercised end to end.
"""

import os
import sys
import types

import pytest

os.environ.setdefault('API_KEY', '/test/api-key')
os.environ.setdefault('SQS_QUEUE_NAME', 'test-queue')

_secrets = types.ModuleType('src.secrets')
_secrets.get_param_value_by_name = lambda name: f'stub:{name}'
sys.modules['src.secrets'] = _secrets

_sqs = types.ModuleType('src.sqs')
_sqs.parse_message = lambda message: message
sys.modules['src.sqs'] = _sqs

import psycopg2  # noqa: E402
from psycopg2 import extensions  # noqa: E402
from psycopg2 import sql as pgsql  # noqa: E402


def render(query) -> str:
    """renders psycopg2.sql composables without a live connection"""
    if isinstance(query, pgsql.Composed):
        return ''.join(render(part) for part in query.seq)
    if isinstance(query, pgsql.SQL):
        return query.string
    if isinstance(query, pgsql.Literal):
        value = query.wrapped
        if value is None:
            return 'NULL'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, (int, float)):
            return str(value)
        return "'" + str(value).replace("'", "''") + "'"
    if isinstance(query, pgsql.Identifier):
        return '.'.join(f'"{s}"' for s in query.strings)
    return str(query)


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self.closed = False
        self.rowcount = 0
        self._result = None

    def mogrify(self, query):
        return render(query)

    def execute(self, query):
        if self.conn.fail_next:
            self.conn.fail_next = False
            raise psycopg2.OperationalError('server closed the connection unexpectedly')
        text = self.mogrify(query)
        self.conn.executed.append(text)
        self.conn.status = extensions.STATUS_IN_TRANSACTION
        self._result = self.conn.results.pop(0) if self.conn.results else []
        self.rowcount = len(self._result)

    def fetchall(self):
        return self._result

    def close(self):
        self.closed = True


class FakeConnection:
    """enough of psycopg2.connection for Database"""

    encoding = 'UTF8'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.closed = 0
        self.status = extensions.STATUS_READY
        self.notices = ['stale notice']
        self.executed = []
        self.results = []
        self.commits = 0
        self.rollbacks = 0
        self.fail_next = False

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1
        self.status = extensions.STATUS_READY

    def rollback(self):
        self.rollbacks += 1
        self.status = extensions.STATUS_READY

    def close(self):
        self.closed = 1


@pytest.fixture
def fake_pg(monkeypatch):
    """patches psycopg2.connect, resets the shared connection, returns the list of connections opened"""
    import src.database as database

    opened = []

    def connect(**kwargs):
        conn = FakeConnection(**kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(database.psycopg2, 'connect', connect)
    monkeypatch.setattr(database, '_conn', None)
    monkeypatch.setattr(database, '_last_used', 0.0)
    monkeypatch.setattr(database, '_column_cache', {})
    return opened
