

CREATE TABLE IF NOT EXISTS fec.filing_amendment_chain (
  filing_amendment_chain_id INT IDENTITY(1,1),
  fec_file_id TEXT NOT NULL,
  amendment_id TEXT NOT NULL,
  PRIMARY KEY(filing_amendment_chain_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE filing_amendment_chain is 'Linking table to connect filings to amendments';
