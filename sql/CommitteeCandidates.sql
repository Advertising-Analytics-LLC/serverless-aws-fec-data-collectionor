--
-- Linking table to connect CommitteeDetail with CandidateDetail
-- See https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__
--
CREATE TABLE IF NOT EXISTS committeecandidates (
  committee_candidate_id INT IDENTITY(1,1),
  committee_id VARCHAR(10),
  candidate_id VARCHAR(10),
  PRIMARY KEY(committee_candidate_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE committeecandidates is 'Linking table to connect CommitteeDetail to CandidateDetail';