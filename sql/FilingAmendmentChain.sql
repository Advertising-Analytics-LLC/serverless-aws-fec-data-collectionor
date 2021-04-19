
SET search_path TO fec;

CREATE TABLE IF NOT EXISTS fec.filing_amendment_chain (
  filing_amendment_chain_id INT IDENTITY(1,1),
  fec_file_id INT NOT NULL,
  amendment_id INT NOT NULL,
  amendment_number INT NOT NULL,
  PRIMARY KEY(filing_amendment_chain_id),
  FOREIGN KEY(fec_file_id) REFERENCES fec.filings(fec_file_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE fec.filing_amendment_chain is 'Linking table to connect filings to amendments';
