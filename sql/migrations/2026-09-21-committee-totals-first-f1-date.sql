-- openFEC added first_f1_date to the committee-totals response. The loader built
-- its column list from the payload keys, so every write to fec.committee_totals
-- failed with UndefinedColumn from roughly 2022 until this was found on 2026-09-17.
--
-- sql/CommitteeTotals.sql is CREATE TABLE IF NOT EXISTS, so it cannot add a column
-- to the existing table. Apply this by hand, then confirm with:
--   select column_name from information_schema.columns
--    where table_schema='fec' and table_name='committee_totals' and column_name='first_f1_date';

ALTER TABLE fec.committee_totals ADD COLUMN first_f1_date VARCHAR(256);
