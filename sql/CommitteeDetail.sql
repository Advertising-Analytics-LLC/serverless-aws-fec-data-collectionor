
--
-- Table structure for table CommitteeDetail generated from model 'CommitteeDetail'
-- See https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
--
CREATE TABLE IF NOT EXISTS committeecandidates (
  committee_candidate_id INT IDENTITY(1,1),
  committee_id VARCHAR(10),
  candidate_id VARCHAR(10),
  PRIMARY KEY(committee_candidate_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE committeecandidates is 'Linking table to connect CommitteeDetail to CandidateDetail';

--
-- Table structure for table CommitteeDetail generated from model 'CommitteeDetail'
-- See https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
--
CREATE TABLE IF NOT EXISTS committeedetail (
  committee_id VARCHAR(10) NOT NULL,
  affiliated_committee_name VARCHAR(MAX) DEFAULT NULL,
  city VARCHAR(MAX) DEFAULT NULL,
  committee_type VARCHAR(MAX) NOT NULL,
  committee_type_full VARCHAR(MAX) DEFAULT NULL,
  custodian_city VARCHAR(MAX) DEFAULT NULL,
  custodian_name_1 VARCHAR(MAX) DEFAULT NULL,
  custodian_name_2 VARCHAR(MAX) DEFAULT NULL,
  custodian_name_full VARCHAR(MAX) DEFAULT NULL,
  custodian_name_middle VARCHAR(MAX) DEFAULT NULL,
  custodian_name_prefix VARCHAR(MAX) DEFAULT NULL,
  custodian_name_suffix VARCHAR(MAX) DEFAULT NULL,
  custodian_name_title VARCHAR(MAX) DEFAULT NULL,
  custodian_phone VARCHAR(MAX) DEFAULT NULL,
  custodian_state VARCHAR(MAX) DEFAULT NULL,
  custodian_street_1 VARCHAR(MAX) DEFAULT NULL,
  custodian_street_2 VARCHAR(MAX) DEFAULT NULL,
  custodian_zip VARCHAR(MAX) DEFAULT NULL,
  -- LIST seperated by ~
  cycles VARCHAR(MAX) DEFAULT NULL,
  designation VARCHAR(MAX) DEFAULT NULL,
  designation_full VARCHAR(MAX) DEFAULT NULL,
  email VARCHAR(MAX) DEFAULT NULL,
  fax VARCHAR(MAX) DEFAULT NULL,
  filing_frequency VARCHAR(MAX) DEFAULT NULL,
  first_file_date DATE DEFAULT NULL,
  form_type VARCHAR(MAX) DEFAULT NULL,
  last_file_date DATE DEFAULT NULL,
  -- NOT IN API SCHEMA
  last_updated TIMESTAMP NOT NULL,
  leadership_pac VARCHAR(MAX) DEFAULT NULL,
  lobbyist_registrant_pac VARCHAR(MAX) DEFAULT NULL,
  -- renamed from name to avoid collision
  committee_name VARCHAR(MAX) DEFAULT NOT NULL,
  organization_type VARCHAR(MAX) DEFAULT NULL,
  organization_type_full VARCHAR(MAX) DEFAULT NULL,
  party VARCHAR(MAX) DEFAULT NULL,
  party_full VARCHAR(MAX) DEFAULT NULL,
  party_type VARCHAR(MAX) DEFAULT NULL,
  party_type_full VARCHAR(MAX) DEFAULT NULL,
  state VARCHAR(MAX) DEFAULT NULL,
  state_full VARCHAR(MAX) DEFAULT NULL,
  street_1 VARCHAR(MAX) DEFAULT NULL,
  street_2 VARCHAR(MAX) DEFAULT NULL,
  treasurer_city VARCHAR(MAX) DEFAULT NULL,
  treasurer_name VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_1 VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_2 VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_middle VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_prefix VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_suffix VARCHAR(MAX) DEFAULT NULL,
  treasurer_name_title VARCHAR(MAX) DEFAULT NULL,
  treasurer_phone VARCHAR(MAX) DEFAULT NULL,
  treasurer_state VARCHAR(MAX) DEFAULT NULL,
  treasurer_street_1 VARCHAR(MAX) DEFAULT NULL,
  treasurer_street_2 VARCHAR(MAX) DEFAULT NULL,
  treasurer_zip VARCHAR(MAX) DEFAULT NULL,
  website VARCHAR(MAX) DEFAULT NULL,
  zip VARCHAR(MAX) DEFAULT NULL,
  primary key(committee_id)
) DISTSTYLE AUTO;
