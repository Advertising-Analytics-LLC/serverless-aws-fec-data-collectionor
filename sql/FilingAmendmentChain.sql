
SET search_path TO fec;

CREATE TABLE IF NOT EXISTS fec.filing_amendment_chain (
	filing_amendment_chain_id int4 NOT null default round(random()*1000000000),
  fec_file_id INT NOT NULL,
  amendment_id INT NOT NULL,
  amendment_number INT NOT NULL,
  PRIMARY KEY(filing_amendment_chain_id),
  FOREIGN KEY(fec_file_id) REFERENCES fec.filings(fec_file_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE fec.filing_amendment_chain is 'Linking table to connect filings to amendments';
