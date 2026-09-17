import re

from src.database import Database
from src.FinancialSummaryLoader import upsert_amendment_chain, upsert_filing


def _inserted_ids(conn):
    inserts = [q for q in conn.executed if q.startswith('INSERT INTO fec.filing_amendment_chain')]
    assert len(inserts) <= 1
    if not inserts:
        return []
    return [(int(a), int(n)) for a, n in re.findall(r"\(\'[^']+\', \d+, (\d+), (\d+)\)", inserts[0])]


def test_only_missing_links_inserted_in_one_statement(fake_pg):
    with Database() as db:
        db.conn.results = [[(10,), (30,)]]  # already linked
        assert upsert_amendment_chain(db, '1427633', ['10', '20', '30', '40']) is True
    conn = fake_pg[0]
    selects = [q for q in conn.executed if q.startswith('SELECT')]
    assert selects == ['SELECT amendment_id FROM fec.filing_amendment_chain WHERE fec_file_id=1427633']
    assert _inserted_ids(conn) == [(20, 1), (40, 3)]  # amendment_number is the position in the chain
    assert conn.commits == 1


def test_nothing_inserted_when_chain_complete(fake_pg):
    with Database() as db:
        db.conn.results = [[(10,), (20,)]]
        assert upsert_amendment_chain(db, '1427633', [10, 20]) is True
    assert _inserted_ids(fake_pg[0]) == []
    assert fake_pg[0].commits == 0


def test_upsert_filing_uses_one_block_and_skips_existing_filing(fake_pg):
    filing = {
        'fec_file_id': 'FEC-1427633',
        'committee_id': 'C00027466',
        'amendment_chain': [1427633, 1500000],
        'additional_bank_names': None,
    }
    with Database() as db:
        pass
    conn = fake_pg[0]
    conn.results = [[(1427633,)], [], [('row',)]]  # chain SELECT, chain INSERT, filing exists
    assert upsert_filing(filing) is True
    assert len(fake_pg) == 1
    assert _inserted_ids(conn) == [(1500000, 1)]
    assert not any(q.startswith('INSERT INTO fec.filings') for q in conn.executed)
    assert conn.rollbacks == 1  # the open read transaction from the exists-check
