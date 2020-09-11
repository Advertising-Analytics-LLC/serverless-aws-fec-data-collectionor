
CREATE TABLE IF NOT EXISTS fec.loading_stats (
    query_time DATE NOT NULL,
    candidate_detail_count INT,
    candidate_detail_min_first_file DATE,
    committee_detail_count INT,
    committee_detail_min_first_file DATE,
    filings_count INT,
    filings_min_receipt_date DATE,
    committee_totals_count INT,
    filing_amendment_chain_count INT,
    filings_schedule_b_count INT,
    filings_schedule_e_count INT,
    form_1_supplemental_count INT
)
