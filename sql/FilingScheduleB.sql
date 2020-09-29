
--
-- Generated from https://github.com/esonderegger/fecfile/blob/master/fecfile/mappings.json
-- with input from these schemas:
-- https://github.com/fecgov/fecfile-online/blob/master/data/migrations/V000047__sched_b.sql
-- https://github.com/fecgov/fecfile-online/blob/master/data/migrations/V000056__sched_b_ddl_update.sql
--
SET search_path TO fec;
CREATE TABLE IF NOT EXISTS fec.filings_schedule_b (
    fec_file_id INT NOT NULL,
    amended_cd VARCHAR(100) DEFAULT NULL,
    back_reference_sched_name VARCHAR(100) DEFAULT NULL,
    back_reference_tran_id_number VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_district VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_fec_id VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_first_name VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_last_name VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_middle_name VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_name VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_office VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_prefix VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_state VARCHAR(100) DEFAULT NULL,
    beneficiary_candidate_suffix VARCHAR(100) DEFAULT NULL,
    beneficiary_committee_fec_id VARCHAR(100) DEFAULT NULL,
    beneficiary_committee_name VARCHAR(200) DEFAULT NULL,
    category_code VARCHAR(100) DEFAULT NULL,
    communication_date VARCHAR(100) DEFAULT NULL,
    conduit_city VARCHAR(100) DEFAULT NULL,
    conduit_name VARCHAR(100) DEFAULT NULL,
    conduit_state VARCHAR(100) DEFAULT NULL,
    conduit_street_1 VARCHAR(100) DEFAULT NULL,
    conduit_street_2 VARCHAR(100) DEFAULT NULL,
    conduit_zip_code VARCHAR(100) DEFAULT NULL,
    election_code VARCHAR(100) DEFAULT NULL,
    election_other_description VARCHAR(100) DEFAULT NULL,
    entity_type VARCHAR(100) DEFAULT NULL,
    expenditure_amount NUMERIC(12,2) DEFAULT NULL,
    expenditure_date DATE DEFAULT NULL,
    expenditure_purpose_code VARCHAR(100) DEFAULT NULL,
    expenditure_purpose_descrip VARCHAR(100) DEFAULT NULL,
    filer_committee_id_number VARCHAR(100) DEFAULT NULL,
    form_type VARCHAR(100) DEFAULT NULL,
    image_number VARCHAR(100) DEFAULT NULL,
    memo_code VARCHAR(100) DEFAULT NULL,
    memo_text_description VARCHAR(100) DEFAULT NULL,
    payee_city VARCHAR(100) DEFAULT NULL,
    payee_first_name VARCHAR(100) DEFAULT NULL,
    payee_last_name VARCHAR(100) DEFAULT NULL,
    payee_middle_name VARCHAR(100) DEFAULT NULL,
    payee_name VARCHAR(100) DEFAULT NULL,
    payee_organization_name VARCHAR(100) DEFAULT NULL,
    payee_prefix VARCHAR(100) DEFAULT NULL,
    payee_state VARCHAR(100) DEFAULT NULL,
    payee_street_1 VARCHAR(100) DEFAULT NULL,
    payee_street_2 VARCHAR(100) DEFAULT NULL,
    payee_suffix VARCHAR(100) DEFAULT NULL,
    payee_zip_code VARCHAR(100) DEFAULT NULL,
    reference_to_si_or_sl_system_code_that_identifies_the_account VARCHAR(100) DEFAULT NULL,
    refund_or_disposal_of_excess VARCHAR(100) DEFAULT NULL,
    semi_annual_refunded_bundled_amt VARCHAR(100) DEFAULT NULL,
    transaction_id_number VARCHAR(25) NOT NULL,
    PRIMARY KEY(transaction_id_number),
    FOREIGN KEY(fec_file_id) REFERENCES fec.filings(fec_file_id),
    FOREIGN KEY (beneficiary_candidate_fec_id) REFERENCES fec.candidate_detail(candidate_id),
    FOREIGN KEY (filer_committee_id_number) REFERENCES fec.committee_detail(committee_id)
) DISTSTYLE AUTO;
