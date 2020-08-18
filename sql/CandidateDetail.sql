--
-- Table structure for table CandidateDetail generated from model 'CandidateDetail'
-- see https://api.open.fec.gov/developers/#/candidate/get_candidate__candidate_id__
--

SET search_path TO 'fec';

CREATE TABLE IF NOT EXISTS fec.candidate_detail (
  active_through INT DEFAULT NULL,
  address_city VARCHAR(100) DEFAULT NULL,
  address_state VARCHAR(2) DEFAULT NULL,
  address_street_1 VARCHAR(200) DEFAULT NULL,
  address_street_2 VARCHAR(200) DEFAULT NULL,
  address_zip VARCHAR(10) DEFAULT NULL,
  candidate_id TEXT DEFAULT NULL,
  candidate_inactive INT DEFAULT NULL,
  candidate_status VARCHAR(1) DEFAULT NULL,
  cycles TEXT DEFAULT NULL,
  district VARCHAR(2) DEFAULT NULL,
  district_number INT DEFAULT NULL,
  election_districts TEXT DEFAULT NULL,
  election_years TEXT DEFAULT NULL,
  federal_funds_flag INT DEFAULT NULL,
  first_file_date DATE DEFAULT NULL,
  flags TEXT DEFAULT NULL,
  has_raised_funds INT DEFAULT NULL,
  incumbent_challenge VARCHAR(1) DEFAULT NULL,
  incumbent_challenge_full VARCHAR(10) DEFAULT NULL,
  last_f2_date DATE DEFAULT NULL,
  last_file_date DATE DEFAULT NULL,
  load_date DATETIME DEFAULT NULL,
  name VARCHAR(100) DEFAULT NULL,
  office VARCHAR(1) DEFAULT NULL,
  office_full VARCHAR(9) DEFAULT NULL,
  party VARCHAR(3) DEFAULT NULL,
  party_full VARCHAR(255) DEFAULT NULL,
  state VARCHAR(2) DEFAULT NULL,
  PRIMARY KEY(candidate_id),
  UNIQUE(candidate_id)
) DISTSTYLE AUTO;
