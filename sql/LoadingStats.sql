
CREATE TABLE IF NOT EXISTS fec.loading_stats (
    query_time DATE NOT NULL,
    candidate_detail_count INT,
    candidate_detail_count_unique INT,
    committee_detail_count INT,
    committee_detail_count_unique INT,
    filings_count INT,
    filings_unique_count INT,
    committee_totals_count INT,
    committee_totals_count_unique INT,
    filing_amendment_chain_count INT,
    filing_amendment_chain_count_unique INT,
    filings_schedule_b_count INT,
    filings_schedule_b_count_uniqe INT,
    filings_schedule_e_count INT,
    filings_schedule_e_count_uniqe INT,
    form_1_supplemental_count INT
    form_1_supplemental_count_uniqe INT
)
