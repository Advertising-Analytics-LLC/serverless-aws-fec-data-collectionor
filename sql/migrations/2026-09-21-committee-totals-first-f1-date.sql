-- openFEC added fields to the committee-totals response. The loader built its
-- column list from the payload keys, so every write to fec.committee_totals failed
-- with UndefinedColumn from roughly 2022 until this was found on 2026-09-17.
--
-- Only first_f1_date ever appeared in the error: Postgres reports the first unknown
-- target column and the old builder sorted keys alphabetically. The live payload was
-- actually missing five columns (checked 2026-09-21 against information_schema):
--   first_f1_date, operating_expenditures_percent,
--   party_and_other_committee_contributions_percent,
--   sponsor_candidate_ids, sponsor_candidate_list
--
-- The first three were added 2026-09-21 (statements below, one ADD COLUMN per
-- ALTER as Redshift requires). VARCHAR(256) matches the existing percent column.
--
-- sponsor_candidate_ids / sponsor_candidate_list are DELIBERATELY NOT ADDED. They
-- are JSON lists (list of ids, list of {id, name} dicts); psycopg2 renders a list
-- as ARRAY[...] and cannot adapt a dict, so a plain VARCHAR column would fail every
-- row for a committee that has a sponsor. Add a condense_dimension() step in
-- FinancialSummaryLoader first (as additional_bank_names has), then the column.
--
-- individual_contributions_percent and organization_type_full were found live but
-- absent from sql/CommitteeTotals.sql: an earlier hand-ALTER that was never recorded.
-- The DDL file now lists them; no statement needed.
--
-- sql/CommitteeTotals.sql is CREATE TABLE IF NOT EXISTS, so it cannot add a column
-- to the existing table. Apply by hand, then confirm with:
--   select column_name from information_schema.columns
--    where table_schema='fec' and table_name='committee_totals'
--      and column_name in ('first_f1_date','operating_expenditures_percent',
--                          'party_and_other_committee_contributions_percent');

ALTER TABLE fec.committee_totals ADD COLUMN first_f1_date VARCHAR(256);
ALTER TABLE fec.committee_totals ADD COLUMN operating_expenditures_percent VARCHAR(256);
ALTER TABLE fec.committee_totals ADD COLUMN party_and_other_committee_contributions_percent VARCHAR(256);
