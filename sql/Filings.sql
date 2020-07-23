--
-- OpenFEC.
-- Prepared SQL queries for 'Filings' definition.
--
--
-- Table structure for table Filings generated from model 'Filings'
--

CREATE TABLE IF NOT EXISTS fec.filings (
  amendment_indicator TEXT DEFAULT NULL,
  amendment_version INT DEFAULT NULL,
  beginning_image_number TEXT DEFAULT NULL,
  candidate_id TEXT DEFAULT NULL,
  candidate_name TEXT DEFAULT NULL,
  cash_on_hand_beginning_period DECIMAL(20, 9) DEFAULT NULL,
  cash_on_hand_end_period DECIMAL(20, 9) DEFAULT NULL,
  committee_id TEXT DEFAULT NULL,
  committee_name TEXT DEFAULT NULL,
  committee_type TEXT DEFAULT NULL,
  coverage_end_date DATE DEFAULT NULL,
  coverage_start_date DATE DEFAULT NULL,
  csv_url TEXT DEFAULT NULL,
  cycle INT DEFAULT NULL,
  debts_owed_by_committee DECIMAL(20, 9) DEFAULT NULL,
  debts_owed_to_committee DECIMAL(20, 9) DEFAULT NULL,
  document_description TEXT DEFAULT NULL,
  document_type TEXT DEFAULT NULL,
  document_type_full TEXT DEFAULT NULL,
  election_year INT DEFAULT NULL,
  ending_image_number TEXT DEFAULT NULL,
  fec_file_id TEXT NOT NULL,
  fec_url TEXT DEFAULT NULL,
  file_number INT DEFAULT NULL,
  form_category TEXT DEFAULT NULL,
  form_type TEXT DEFAULT NULL,
  house_personal_funds DECIMAL(20, 9) DEFAULT NULL,
  html_url TEXT DEFAULT NULL,
  is_amended TINYINT(1) DEFAULT NULL,
  means_filed TEXT DEFAULT NULL,
  most_recent TINYINT(1) DEFAULT NULL,
  most_recent_file_number INT DEFAULT NULL,
  net_donations DECIMAL(20, 9) DEFAULT NULL,
  office TEXT DEFAULT NULL,
  opposition_personal_funds DECIMAL(20, 9) DEFAULT NULL,
  pages INT DEFAULT NULL,
  party TEXT DEFAULT NULL,
  pdf_url TEXT DEFAULT NULL,
  previous_file_number INT DEFAULT NULL,
  primary_general_indicator TEXT DEFAULT NULL,
  receipt_date DATE DEFAULT NULL,
  report_type TEXT DEFAULT NULL,
  report_type_full TEXT DEFAULT NULL,
  report_year INT DEFAULT NULL,
  request_type TEXT DEFAULT NULL,
  senate_personal_funds DECIMAL(20, 9) DEFAULT NULL,
  state TEXT DEFAULT NULL,
  sub_id TEXT DEFAULT NULL,
  total_communication_cost DECIMAL(20, 9) DEFAULT NULL,
  total_disbursements DECIMAL(20, 9) DEFAULT NULL,
  total_independent_expenditures DECIMAL(20, 9) DEFAULT NULL,
  total_individual_contributions DECIMAL(20, 9) DEFAULT NULL,
  total_receipts DECIMAL(20, 9) DEFAULT NULL,
  treasurer_name TEXT DEFAULT NULL,
  update_date DATE DEFAULT NULL,
  PRIMARY KEY(fec_file_id),
  UNIQUE(fec_file_id)
) DISTSTYLE AUTO;
