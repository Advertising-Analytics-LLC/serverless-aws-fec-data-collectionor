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



-- --
-- -- SELECT template for table CommitteeTotals
-- --
-- SELECT all_loans_received, all_other_loans, allocated_federal_election_levin_share, candidate_contribution, cash_on_hand_beginning_period, committee_designation, committee_designation_full, committee_id, committee_name, committee_type, committee_type_full, contribution_refunds, contributions, convention_exp, coordinated_expenditures_by_party_committee, coverage_end_date, coverage_start_date, cycle, disbursements, exempt_legal_accounting_disbursement, exp_prior_years_subject_limits, exp_subject_limits, fed_candidate_committee_contributions, fed_candidate_contribution_refunds, fed_disbursements, fed_election_activity, fed_operating_expenditures, fed_receipts, federal_funds, fundraising_disbursements, independent_expenditures, individual_contributions, individual_itemized_contributions, individual_unitemized_contributions, itemized_convention_exp, itemized_other_disb, itemized_other_income, itemized_other_refunds, itemized_refunds_relating_convention_exp, last_beginning_image_number, last_cash_on_hand_end_period, last_debts_owed_by_committee, last_debts_owed_to_committee, last_report_type_full, last_report_year, loan_repayments, loan_repayments_candidate_loans, loan_repayments_made, loan_repayments_other_loans, loan_repayments_received, loans, loans_and_loan_repayments_made, loans_and_loan_repayments_received, loans_made, loans_made_by_candidate, loans_received, loans_received_from_candidate, net_contributions, net_operating_expenditures, non_allocated_fed_election_activity, offsets_to_fundraising_expenditures, offsets_to_legal_accounting, offsets_to_operating_expenditures, operating_expenditures, other_disbursements, other_fed_operating_expenditures, other_fed_receipts, other_loans_received, other_political_committee_contributions, other_receipts, other_refunds, party_full, pdf_url, political_party_committee_contributions, receipts, refunded_individual_contributions, refunded_other_political_committee_contributions, refunded_political_party_committee_contributions, refunds_relating_convention_exp, repayments_loans_made_by_candidate, repayments_other_loans, report_form, shared_fed_activity, shared_fed_activity_nonfed, shared_fed_operating_expenditures, shared_nonfed_operating_expenditures, total_exp_subject_limits, total_independent_contributions, total_independent_expenditures, total_offsets_to_operating_expenditures, total_transfers, transaction_coverage_date, transfers_from_affiliated_committee, transfers_from_affiliated_party, transfers_from_nonfed_account, transfers_from_nonfed_levin, transfers_from_other_authorized_committee, transfers_to_affiliated_committee, transfers_to_other_authorized_committee, unitemized_convention_exp, unitemized_other_disb, unitemized_other_income, unitemized_other_refunds, unitemized_refunds_relating_convention_exp FROM CommitteeTotals WHERE 1;

-- --
-- -- INSERT template for table CommitteeTotals
-- --
-- INSERT INTO CommitteeTotals(all_loans_received, all_other_loans, allocated_federal_election_levin_share, candidate_contribution, cash_on_hand_beginning_period, committee_designation, committee_designation_full, committee_id, committee_name, committee_type, committee_type_full, contribution_refunds, contributions, convention_exp, coordinated_expenditures_by_party_committee, coverage_end_date, coverage_start_date, cycle, disbursements, exempt_legal_accounting_disbursement, exp_prior_years_subject_limits, exp_subject_limits, fed_candidate_committee_contributions, fed_candidate_contribution_refunds, fed_disbursements, fed_election_activity, fed_operating_expenditures, fed_receipts, federal_funds, fundraising_disbursements, independent_expenditures, individual_contributions, individual_itemized_contributions, individual_unitemized_contributions, itemized_convention_exp, itemized_other_disb, itemized_other_income, itemized_other_refunds, itemized_refunds_relating_convention_exp, last_beginning_image_number, last_cash_on_hand_end_period, last_debts_owed_by_committee, last_debts_owed_to_committee, last_report_type_full, last_report_year, loan_repayments, loan_repayments_candidate_loans, loan_repayments_made, loan_repayments_other_loans, loan_repayments_received, loans, loans_and_loan_repayments_made, loans_and_loan_repayments_received, loans_made, loans_made_by_candidate, loans_received, loans_received_from_candidate, net_contributions, net_operating_expenditures, non_allocated_fed_election_activity, offsets_to_fundraising_expenditures, offsets_to_legal_accounting, offsets_to_operating_expenditures, operating_expenditures, other_disbursements, other_fed_operating_expenditures, other_fed_receipts, other_loans_received, other_political_committee_contributions, other_receipts, other_refunds, party_full, pdf_url, political_party_committee_contributions, receipts, refunded_individual_contributions, refunded_other_political_committee_contributions, refunded_political_party_committee_contributions, refunds_relating_convention_exp, repayments_loans_made_by_candidate, repayments_other_loans, report_form, shared_fed_activity, shared_fed_activity_nonfed, shared_fed_operating_expenditures, shared_nonfed_operating_expenditures, total_exp_subject_limits, total_independent_contributions, total_independent_expenditures, total_offsets_to_operating_expenditures, total_transfers, transaction_coverage_date, transfers_from_affiliated_committee, transfers_from_affiliated_party, transfers_from_nonfed_account, transfers_from_nonfed_levin, transfers_from_other_authorized_committee, transfers_to_affiliated_committee, transfers_to_other_authorized_committee, unitemized_convention_exp, unitemized_other_disb, unitemized_other_income, unitemized_other_refunds, unitemized_refunds_relating_convention_exp)
-- VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});

-- --
-- -- UPDATE template for table CommitteeTotals
-- --
-- UPDATE CommitteeTotals SET all_loans_received = {}, all_other_loans = {}, allocated_federal_election_levin_share = {}, candidate_contribution = {}, cash_on_hand_beginning_period = {}, committee_designation = {}, committee_designation_full = {}, committee_id = {}, committee_name = {}, committee_type = {}, committee_type_full = {}, contribution_refunds = {}, contributions = {}, convention_exp = {}, coordinated_expenditures_by_party_committee = {}, coverage_end_date = {}, coverage_start_date = {}, cycle = {}, disbursements = {}, exempt_legal_accounting_disbursement = {}, exp_prior_years_subject_limits = {}, exp_subject_limits = {}, fed_candidate_committee_contributions = {}, fed_candidate_contribution_refunds = {}, fed_disbursements = {}, fed_election_activity = {}, fed_operating_expenditures = {}, fed_receipts = {}, federal_funds = {}, fundraising_disbursements = {}, independent_expenditures = {}, individual_contributions = {}, individual_itemized_contributions = {}, individual_unitemized_contributions = {}, itemized_convention_exp = {}, itemized_other_disb = {}, itemized_other_income = {}, itemized_other_refunds = {}, itemized_refunds_relating_convention_exp = {}, last_beginning_image_number = {}, last_cash_on_hand_end_period = {}, last_debts_owed_by_committee = {}, last_debts_owed_to_committee = {}, last_report_type_full = {}, last_report_year = {}, loan_repayments = {}, loan_repayments_candidate_loans = {}, loan_repayments_made = {}, loan_repayments_other_loans = {}, loan_repayments_received = {}, loans = {}, loans_and_loan_repayments_made = {}, loans_and_loan_repayments_received = {}, loans_made = {}, loans_made_by_candidate = {}, loans_received = {}, loans_received_from_candidate = {}, net_contributions = {}, net_operating_expenditures = {}, non_allocated_fed_election_activity = {}, offsets_to_fundraising_expenditures = {}, offsets_to_legal_accounting = {}, offsets_to_operating_expenditures = {}, operating_expenditures = {}, other_disbursements = {}, other_fed_operating_expenditures = {}, other_fed_receipts = {}, other_loans_received = {}, other_political_committee_contributions = {}, other_receipts = {}, other_refunds = {}, party_full = {}, pdf_url = {}, political_party_committee_contributions = {}, receipts = {}, refunded_individual_contributions = {}, refunded_other_political_committee_contributions = {}, refunded_political_party_committee_contributions = {}, refunds_relating_convention_exp = {}, repayments_loans_made_by_candidate = {}, repayments_other_loans = {}, report_form = {}, shared_fed_activity = {}, shared_fed_activity_nonfed = {}, shared_fed_operating_expenditures = {}, shared_nonfed_operating_expenditures = {}, total_exp_subject_limits = {}, total_independent_contributions = {}, total_independent_expenditures = {}, total_offsets_to_operating_expenditures = {}, total_transfers = {}, transaction_coverage_date = {}, transfers_from_affiliated_committee = {}, transfers_from_affiliated_party = {}, transfers_from_nonfed_account = {}, transfers_from_nonfed_levin = {}, transfers_from_other_authorized_committee = {}, transfers_to_affiliated_committee = {}, transfers_to_other_authorized_committee = {}, unitemized_convention_exp = {}, unitemized_other_disb = {}, unitemized_other_income = {}, unitemized_other_refunds = {}, unitemized_refunds_relating_convention_exp = {} WHERE 1;

-- --
-- -- DELETE template for table CommitteeTotals
-- --
-- DELETE FROM CommitteeTotals WHERE 0;
