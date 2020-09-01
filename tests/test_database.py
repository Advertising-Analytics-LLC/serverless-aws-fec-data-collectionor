#!/bin/env python3
"""
tests src/database.py
"""

import os
import logging
import pytest
from psycopg2 import sql
from src.database import Database

logger = logging.getLogger(__name__)
pytest.main(args=['-s', os.path.abspath(__file__)])


def test_can_enter_and_exit():
    with Database() as db_obj:
        assert True
        return
    assert False


def test_database_can_query():
    with Database() as db_obj:
        hello_world_query="SELECT 'HELLO WORLD'"
        query_results = db_obj._query(hello_world_query)
        hello_world = query_results[0][0]
    assert hello_world == 'HELLO WORLD'
