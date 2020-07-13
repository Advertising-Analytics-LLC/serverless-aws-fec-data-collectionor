
CREATE TABLE IF NOT EXISTS CommitteeCandidates (
  committee_candidate_id INTEGER,
  committee_id VARCHAR(8),
  candidate_id VARCHAR(10),
  PRIMARY KEY(committee_candidate_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE CommitteeCandidates is 'Linking table to connect CommitteeDetail to CandidateDetail';

--
-- Table structure for table CommitteeDetail generated from model 'CommitteeDetail'
-- See https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
--
CREATE TABLE IF NOT EXISTS CommitteeDetail (
  committee_id VARCHAR(8) NOT NULL ,
  affiliated_committee_name VARCHAR(100) DEFAULT NULL ,
  -- LIST, in linked table
  committee_candidate_id INTEGER DEFAULT NULL,
  city VARCHAR(50) DEFAULT NULL ,
  -- PK
  committee_type VARCHAR(1) NOT NULL,
  committee_type_full VARCHAR(50) DEFAULT NULL,
  custodian_city VARCHAR(50) DEFAULT NULL ,
  custodian_name_1 VARCHAR(50) DEFAULT NULL ,
  custodian_name_2 VARCHAR(50) DEFAULT NULL ,
  custodian_name_full VARCHAR(100) DEFAULT NULL ,
  custodian_name_middle VARCHAR(50) DEFAULT NULL ,
  custodian_name_prefix VARCHAR(50) DEFAULT NULL ,
  custodian_name_suffix VARCHAR(50) DEFAULT NULL ,
  custodian_name_title VARCHAR(50) DEFAULT NULL ,
  custodian_phone VARCHAR(15) DEFAULT NULL ,
  custodian_state VARCHAR(2) DEFAULT NULL ,
  custodian_street_1 VARCHAR(50) DEFAULT NULL ,
  custodian_street_2 VARCHAR(50) DEFAULT NULL ,
  custodian_zip VARCHAR(9) DEFAULT NULL ,
  -- LIST seperated by ~
  cycles VARCHAR(200) DEFAULT NULL,
  designation VARCHAR(1) DEFAULT NULL,
  designation_full VARCHAR(25) DEFAULT NULL,
  email VARCHAR(50) DEFAULT NULL ,
  fax VARCHAR(10) DEFAULT NULL ,
  filing_frequency VARCHAR(1) DEFAULT NULL ,
  first_file_date DATE DEFAULT NULL ,
  form_type VARCHAR(3) DEFAULT NULL ,
  last_file_date DATE DEFAULT NULL ,
  -- NOT IN API SCHEMA
  last_updated TIMESTAMP NOT NULL ,
  leadership_pac VARCHAR(50) DEFAULT NULL ,
  lobbyist_registrant_pac VARCHAR(1) DEFAULT NULL ,
  -- renamed from name to avoid collision
  committee_name VARCHAR(100) DEFAULT NULL,
  organization_type VARCHAR(1) DEFAULT NULL ,
  organization_type_full VARCHAR(100) DEFAULT NULL ,
  party VARCHAR(3) DEFAULT NULL ,
  party_full VARCHAR(50) DEFAULT NULL ,
  party_type VARCHAR(3) DEFAULT NULL ,
  party_type_full VARCHAR(15) DEFAULT NULL ,
  state VARCHAR(2) DEFAULT NULL ,
  state_full VARCHAR(50) DEFAULT NULL ,
  street_1 VARCHAR(50) DEFAULT NULL ,
  street_2 VARCHAR(50) DEFAULT NULL ,
  treasurer_city VARCHAR(50) DEFAULT NULL ,
  treasurer_name VARCHAR(100) DEFAULT NULL ,
  treasurer_name_1 VARCHAR(50) DEFAULT NULL ,
  treasurer_name_2 VARCHAR(50) DEFAULT NULL ,
  treasurer_name_middle VARCHAR(50) DEFAULT NULL ,
  treasurer_name_prefix VARCHAR(50) DEFAULT NULL ,
  treasurer_name_suffix VARCHAR(50) DEFAULT NULL ,
  treasurer_name_title VARCHAR(50) DEFAULT NULL ,
  treasurer_phone VARCHAR(15) DEFAULT NULL ,
  treasurer_state VARCHAR(50) DEFAULT NULL ,
  treasurer_street_1 VARCHAR(50) DEFAULT NULL ,
  treasurer_street_2 VARCHAR(50) DEFAULT NULL ,
  treasurer_zip VARCHAR(9) DEFAULT NULL ,
  website VARCHAR(50) DEFAULT NULL ,
  zip VARCHAR(9) DEFAULT NULL ,
  primary key(committee_id)
) DISTSTYLE AUTO;
