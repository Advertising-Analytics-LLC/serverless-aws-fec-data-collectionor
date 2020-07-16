
import os
import logging
import pytest
from psycopg2 import sql
from src.database import Database

logger = logging.getLogger(__name__)
pytest.main(args=['-s', os.path.abspath(__file__)])


tables=['CommitteeCandidates.sql', 'CommitteeDetail.sql']
table_sqls=[]
for table in tables:
    with open(f'sql/{table}') as fh:
        table_sqls.append(fh.read())

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

# error: create table statment does not return result
# def test_for_table_structure_drift():
#     with Database() as db_obj:
#         for table_sql in table_sqls:
#             query_results = db_obj._query(sql.SQL(table_sql))

#         assert query_results is table_sql
#         return
#     assert False

def test_database_for_duplicate_committeedetail():
    expected_query_result = 1
    with Database() as db_obj:
        max_num_dups_query = 'SELECT count(*) from fec.committeedetail group by committee_id order by count(*) desc limit 1'
        query_results = db_obj._query(max_num_dups_query)
    assert query_results[0][0] == expected_query_result

def test_database_for_duplicate_committeecandidates():
    query = '''
SELECT count(*)
from fec.committeecandidates
group by committee_id, candidate_id
order by count(*) desc
limit 1;
'''
    expected_query_result = 1
    with Database() as db_obj:
        query_results = db_obj._query(query)
        assert query_results[0][0] == expected_query_result
        return
    assert False
