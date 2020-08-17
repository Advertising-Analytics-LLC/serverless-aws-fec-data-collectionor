--
-- Linking table to connect CommitteeDetail with CandidateDetail
-- See https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
--

SET search_path TO fec;

CREATE TABLE IF NOT EXISTS fec.committee_candidate (
  committee_candidate_id INT IDENTITY(1,1),
  committee_id VARCHAR(10),
  candidate_id VARCHAR(10),
  PRIMARY KEY(committee_candidate_id),
  FOREIGN KEY(committee_id) REFERENCES fec.committee_detail(committee_id),
  FOREIGN KEY(candidate_id) REFERENCES fec.candidate_detail(candidate_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE fec.committee_candidate is 'Linking table to connect CommitteeDetail to CandidateDetail';
