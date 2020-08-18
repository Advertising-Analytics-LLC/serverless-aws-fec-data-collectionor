
--
-- Generated from https://github.com/esonderegger/fecfile/blob/master/fecfile/mappings.json
-- from key "^f1s"
--

SET search_path TO fec;

CREATE TABLE IF NOT EXISTS fec.form_1_supplemental (
    fec_file_id INT NOT NULL,
    affiliated_candidate_id_number VARCHAR(100) DEFAULT NULL,
    affiliated_city VARCHAR(100) DEFAULT NULL,
    affiliated_committee_id_number VARCHAR(100) DEFAULT NULL,
    affiliated_committee_name VARCHAR(100) DEFAULT NULL,
    affiliated_first_name VARCHAR(100) DEFAULT NULL,
    affiliated_last_name VARCHAR(100) DEFAULT NULL,
    affiliated_middle_name VARCHAR(100) DEFAULT NULL,
    affiliated_organization_type VARCHAR(100) DEFAULT NULL,
    affiliated_prefix VARCHAR(100) DEFAULT NULL,
    affiliated_relationship_code VARCHAR(100) DEFAULT NULL,
    affiliated_state VARCHAR(100) DEFAULT NULL,
    affiliated_street_1 VARCHAR(100) DEFAULT NULL,
    affiliated_street_2 VARCHAR(100) DEFAULT NULL,
    affiliated_suffix VARCHAR(100) DEFAULT NULL,
    affiliated_zip_code VARCHAR(100) DEFAULT NULL,
    agent_city VARCHAR(100) DEFAULT NULL,
    agent_first_name VARCHAR(100) DEFAULT NULL,
    agent_last_name VARCHAR(100) DEFAULT NULL,
    agent_middle_name VARCHAR(100) DEFAULT NULL,
    agent_prefix VARCHAR(100) DEFAULT NULL,
    agent_state VARCHAR(100) DEFAULT NULL,
    agent_street_1 VARCHAR(100) DEFAULT NULL,
    agent_street_2 VARCHAR(100) DEFAULT NULL,
    agent_suffix VARCHAR(100) DEFAULT NULL,
    agent_telephone VARCHAR(100) DEFAULT NULL,
    agent_title VARCHAR(100) DEFAULT NULL,
    agent_zip_code VARCHAR(100) DEFAULT NULL,
    bank_city VARCHAR(100) DEFAULT NULL,
    bank_name VARCHAR(100) DEFAULT NULL,
    bank_state VARCHAR(100) DEFAULT NULL,
    bank_street_1 VARCHAR(100) DEFAULT NULL,
    bank_street_2 VARCHAR(100) DEFAULT NULL,
    bank_zip_code VARCHAR(100) DEFAULT NULL,
    beginning_image_number VARCHAR(100) DEFAULT NULL,
    filer_committee_id_number VARCHAR(100) DEFAULT NULL,
    form_type VARCHAR(100) DEFAULT NULL,
    joint_fund_participant_committee_id_number VARCHAR(100) DEFAULT NULL,
    joint_fund_participant_committee_name VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY(fec_file_id) REFERENCES fec.filings(fec_file_id),
    FOREIGN KEY(affiliated_candidate_id_number) REFERENCES fec.candidate_detail(candidate_id),
    FOREIGN KEY(affiliated_committee_id_number) REFERENCES fec.committee_detail(committee_id),
    FOREIGN KEY(filer_committee_id_number) REFERENCES fec.committee_detail(committee_id),
    FOREIGN KEY(joint_fund_participant_committee_id_number) REFERENCES fec.committee_detail(committee_id)
) DISTSTYLE AUTO;
