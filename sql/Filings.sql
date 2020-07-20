--
-- OpenFEC.
-- Prepared SQL queries for 'Filings' definition.
--
--
-- Table structure for table Filings generated from model 'Filings'
--

CREATE TABLE IF NOT EXISTS fec.filing_amendment_chain (
  filing_amendment_chain_id INT IDENTITY(1,1),
  PRIMARY KEY(filing_amendment_chain_id)
) DISTSTYLE AUTO;

COMMENT ON TABLE filing_amendment_chain is 'Linking table to connect filings to amendments';

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
  fec_file_id TEXT DEFAULT NULL,
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
  update_date DATE DEFAULT NULL
) DISTSTYLE AUTO;


-- --
-- -- SELECT template for table Filings
-- --
-- SELECT amendment_chain, amendment_indicator, amendment_version, beginning_image_number, candidate_id, candidate_name, cash_on_hand_beginning_period, cash_on_hand_end_period, committee_id, committee_name, committee_type, coverage_end_date, coverage_start_date, csv_url, cycle, debts_owed_by_committee, debts_owed_to_committee, document_description, document_type, document_type_full, election_year, ending_image_number, fec_file_id, fec_url, file_number, form_category, form_type, house_personal_funds, html_url, is_amended, means_filed, most_recent, most_recent_file_number, net_donations, office, opposition_personal_funds, pages, party, pdf_url, previous_file_number, primary_general_indicator, receipt_date, report_type, report_type_full, report_year, request_type, senate_personal_funds, state, sub_id, total_communication_cost, total_disbursements, total_independent_expenditures, total_individual_contributions, total_receipts, treasurer_name, update_date FROM Filings WHERE 1;

-- --
-- -- INSERT template for table Filings
-- --
-- INSERT INTO
-- Filings(amendment_chain, amendment_indicator, amendment_version, beginning_image_number, candidate_id, candidate_name, cash_on_hand_beginning_period, cash_on_hand_end_period, committee_id, committee_name, committee_type, coverage_end_date, coverage_start_date, csv_url, cycle, debts_owed_by_committee, debts_owed_to_committee, document_description, document_type, document_type_full, election_year, ending_image_number, fec_file_id, fec_url, file_number, form_category, form_type, house_personal_funds, html_url, is_amended, means_filed, most_recent, most_recent_file_number, net_donations, office, opposition_personal_funds, pages, party, pdf_url, previous_file_number, primary_general_indicator, receipt_date, report_type, report_type_full, report_year, request_type, senate_personal_funds, state, sub_id, total_communication_cost, total_disbursements, total_independent_expenditures, total_individual_contributions, total_receipts, treasurer_name, update_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- --
-- -- UPDATE template for table Filings
-- --
-- UPDATE Filings SET amendment_chain = %s, amendment_indicator = %s, amendment_version = %s, beginning_image_number = %s, candidate_id = %s, candidate_name = %s, cash_on_hand_beginning_period = %s, cash_on_hand_end_period = %s, committee_id = %s, committee_name = %s, committee_type = %s, coverage_end_date = %s, coverage_start_date = %s, csv_url = %s, cycle = %s, debts_owed_by_committee = %s, debts_owed_to_committee = %s, document_description = %s, document_type = %s, document_type_full = %s, election_year = %s, ending_image_number = %s, fec_file_id = %s, fec_url = %s, file_number = %s, form_category = %s, form_type = %s, house_personal_funds = %s, html_url = %s, is_amended = %s, means_filed = %s, most_recent = %s, most_recent_file_number = %s, net_donations = %s, office = %s, opposition_personal_funds = %s, pages = %s, party = %s, pdf_url = %s, previous_file_number = %s, primary_general_indicator = %s, receipt_date = %s, report_type = %s, report_type_full = %s, report_year = %s, request_type = %s, senate_personal_funds = %s, state = %s, sub_id = %s, total_communication_cost = %s, total_disbursements = %s, total_independent_expenditures = %s, total_individual_contributions = %s, total_receipts = %s, treasurer_name = %s, update_date = %s WHERE 1;

-- --
-- -- DELETE template for table Filings
-- --
-- DELETE FROM Filings WHERE 0;
