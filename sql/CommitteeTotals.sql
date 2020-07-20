--
-- OpenFEC.
-- Prepared SQL queries for 'CommitteeTotals' definition.
--
--
-- Table structure for table CommitteeTotals generated from model 'CommitteeTotals'
--

CREATE TABLE IF NOT EXISTS committee_totals (
  all_loans_received DECIMAL(20, 9) DEFAULT NULL,
  all_other_loans DECIMAL(20, 9) DEFAULT NULL,
  allocated_federal_election_levin_share DECIMAL(20, 9) DEFAULT NULL,
  candidate_contribution DECIMAL(20, 9) DEFAULT NULL,
  cash_on_hand_beginning_period DECIMAL(20, 9) DEFAULT NULL,
  committee_designation TEXT DEFAULT NULL,
  committee_designation_full TEXT DEFAULT NULL,
  committee_id TEXT DEFAULT NULL,
  committee_name TEXT DEFAULT NULL,
  committee_type TEXT DEFAULT NULL,
  committee_type_full TEXT DEFAULT NULL,
  contribution_refunds DECIMAL(20, 9) DEFAULT NULL,
  contributions DECIMAL(20, 9) DEFAULT NULL,
  convention_exp DECIMAL(20, 9) DEFAULT NULL,
  coordinated_expenditures_by_party_committee DECIMAL(20, 9) DEFAULT NULL,
  coverage_end_date DATETIME DEFAULT NULL,
  coverage_start_date DATETIME DEFAULT NULL,
  cycle INT NOT NULL,
  disbursements DECIMAL(20, 9) DEFAULT NULL,
  exempt_legal_accounting_disbursement DECIMAL(20, 9) DEFAULT NULL,
  exp_prior_years_subject_limits DECIMAL(20, 9) DEFAULT NULL,
  exp_subject_limits DECIMAL(20, 9) DEFAULT NULL,
  fed_candidate_committee_contributions DECIMAL(20, 9) DEFAULT NULL,
  fed_candidate_contribution_refunds DECIMAL(20, 9) DEFAULT NULL,
  fed_disbursements DECIMAL(20, 9) DEFAULT NULL,
  fed_election_activity DECIMAL(20, 9) DEFAULT NULL,
  fed_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  fed_receipts DECIMAL(20, 9) DEFAULT NULL,
  federal_funds DECIMAL(20, 9) DEFAULT NULL,
  fundraising_disbursements DECIMAL(20, 9) DEFAULT NULL,
  independent_expenditures DECIMAL(20, 9) DEFAULT NULL,
  individual_contributions DECIMAL(20, 9) DEFAULT NULL,
  individual_itemized_contributions DECIMAL(20, 9) DEFAULT NULL,
  individual_unitemized_contributions DECIMAL(20, 9) DEFAULT NULL,
  itemized_convention_exp DECIMAL(20, 9) DEFAULT NULL,
  itemized_other_disb DECIMAL(20, 9) DEFAULT NULL,
  itemized_other_income DECIMAL(20, 9) DEFAULT NULL,
  itemized_other_refunds DECIMAL(20, 9) DEFAULT NULL,
  itemized_refunds_relating_convention_exp DECIMAL(20, 9) DEFAULT NULL,
  last_beginning_image_number TEXT DEFAULT NULL,
  last_cash_on_hand_end_period DECIMAL(20, 9) DEFAULT NULL,
  last_debts_owed_by_committee DECIMAL(20, 9) DEFAULT NULL,
  last_debts_owed_to_committee DECIMAL(20, 9) DEFAULT NULL,
  last_report_type_full TEXT DEFAULT NULL,
  last_report_year INT DEFAULT NULL,
  loan_repayments DECIMAL(20, 9) DEFAULT NULL,
  loan_repayments_candidate_loans DECIMAL(20, 9) DEFAULT NULL,
  loan_repayments_made DECIMAL(20, 9) DEFAULT NULL,
  loan_repayments_other_loans DECIMAL(20, 9) DEFAULT NULL,
  loan_repayments_received DECIMAL(20, 9) DEFAULT NULL,
  loans DECIMAL(20, 9) DEFAULT NULL,
  loans_and_loan_repayments_made DECIMAL(20, 9) DEFAULT NULL,
  loans_and_loan_repayments_received DECIMAL(20, 9) DEFAULT NULL,
  loans_made DECIMAL(20, 9) DEFAULT NULL,
  loans_made_by_candidate DECIMAL(20, 9) DEFAULT NULL,
  loans_received DECIMAL(20, 9) DEFAULT NULL,
  loans_received_from_candidate DECIMAL(20, 9) DEFAULT NULL,
  net_contributions DECIMAL(20, 9) DEFAULT NULL,
  net_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  non_allocated_fed_election_activity DECIMAL(20, 9) DEFAULT NULL,
  offsets_to_fundraising_expenditures DECIMAL(20, 9) DEFAULT NULL,
  offsets_to_legal_accounting DECIMAL(20, 9) DEFAULT NULL,
  offsets_to_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  other_disbursements DECIMAL(20, 9) DEFAULT NULL,
  other_fed_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  other_fed_receipts DECIMAL(20, 9) DEFAULT NULL,
  other_loans_received DECIMAL(20, 9) DEFAULT NULL,
  other_political_committee_contributions DECIMAL(20, 9) DEFAULT NULL,
  other_receipts DECIMAL(20, 9) DEFAULT NULL,
  other_refunds DECIMAL(20, 9) DEFAULT NULL,
  party_full TEXT DEFAULT NULL,
  pdf_url TEXT DEFAULT NULL,
  political_party_committee_contributions DECIMAL(20, 9) DEFAULT NULL,
  receipts DECIMAL(20, 9) DEFAULT NULL,
  refunded_individual_contributions DECIMAL(20, 9) DEFAULT NULL,
  refunded_other_political_committee_contributions DECIMAL(20, 9) DEFAULT NULL,
  refunded_political_party_committee_contributions DECIMAL(20, 9) DEFAULT NULL,
  refunds_relating_convention_exp DECIMAL(20, 9) DEFAULT NULL,
  repayments_loans_made_by_candidate DECIMAL(20, 9) DEFAULT NULL,
  repayments_other_loans DECIMAL(20, 9) DEFAULT NULL,
  report_form TEXT DEFAULT NULL,
  shared_fed_activity DECIMAL(20, 9) DEFAULT NULL,
  shared_fed_activity_nonfed DECIMAL(20, 9) DEFAULT NULL,
  shared_fed_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  shared_nonfed_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  total_exp_subject_limits DECIMAL(20, 9) DEFAULT NULL,
  total_independent_contributions DECIMAL(20, 9) DEFAULT NULL,
  total_independent_expenditures DECIMAL(20, 9) DEFAULT NULL,
  total_offsets_to_operating_expenditures DECIMAL(20, 9) DEFAULT NULL,
  total_transfers DECIMAL(20, 9) DEFAULT NULL,
  transaction_coverage_date DATE DEFAULT NULL,
  transfers_from_affiliated_committee DECIMAL(20, 9) DEFAULT NULL,
  transfers_from_affiliated_party DECIMAL(20, 9) DEFAULT NULL,
  transfers_from_nonfed_account DECIMAL(20, 9) DEFAULT NULL,
  transfers_from_nonfed_levin DECIMAL(20, 9) DEFAULT NULL,
  transfers_from_other_authorized_committee DECIMAL(20, 9) DEFAULT NULL,
  transfers_to_affiliated_committee DECIMAL(20, 9) DEFAULT NULL,
  transfers_to_other_authorized_committee DECIMAL(20, 9) DEFAULT NULL,
  unitemized_convention_exp DECIMAL(20, 9) DEFAULT NULL,
  unitemized_other_disb DECIMAL(20, 9) DEFAULT NULL,
  unitemized_other_income DECIMAL(20, 9) DEFAULT NULL,
  unitemized_other_refunds DECIMAL(20, 9) DEFAULT NULL,
  unitemized_refunds_relating_convention_exp DECIMAL(20, 9) DEFAULT NULL
) DISTSTYLE AUTO;
