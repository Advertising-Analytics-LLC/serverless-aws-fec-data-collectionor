

--DROP TABLE fec.filings;
CREATE TABLE IF NOT EXISTS fec.filings
(
	amendment_indicator VARCHAR(256)   ENCODE lzo
	,amendment_version INTEGER   ENCODE az64
	,beginning_image_number VARCHAR(256)   ENCODE lzo
	,candidate_id VARCHAR(256)   ENCODE lzo
	,candidate_name VARCHAR(256)   ENCODE lzo
	,cash_on_hand_beginning_period NUMERIC(20,9)   ENCODE az64
	,cash_on_hand_end_period NUMERIC(20,9)   ENCODE az64
	,committee_id VARCHAR(256)   ENCODE lzo
	,committee_name VARCHAR(256)   ENCODE lzo
	,committee_type VARCHAR(256)   ENCODE lzo
	,coverage_end_date DATE   ENCODE az64
	,coverage_start_date DATE   ENCODE az64
	,csv_url VARCHAR(256)   ENCODE lzo
	,"cycle" INTEGER   ENCODE az64
	,debts_owed_by_committee NUMERIC(20,9)   ENCODE az64
	,debts_owed_to_committee NUMERIC(20,9)   ENCODE az64
	,document_description VARCHAR(256)   ENCODE lzo
	,document_type VARCHAR(256)   ENCODE lzo
	,document_type_full VARCHAR(256)   ENCODE lzo
	,election_year INTEGER   ENCODE az64
	,ending_image_number VARCHAR(256)   ENCODE lzo
	,fec_file_id INTEGER NOT NULL  ENCODE az64
	,fec_url VARCHAR(256)   ENCODE lzo
	,file_number INTEGER   ENCODE az64
	,form_category VARCHAR(256)   ENCODE lzo
	,form_type VARCHAR(256)   ENCODE lzo
	,house_personal_funds NUMERIC(20,9)   ENCODE az64
	,html_url VARCHAR(256)   ENCODE lzo
	,is_amended INTEGER   ENCODE az64
	,means_filed VARCHAR(256)   ENCODE lzo
	,most_recent INTEGER   ENCODE az64
	,most_recent_file_number INTEGER   ENCODE az64
	,net_donations NUMERIC(20,9)   ENCODE az64
	,office VARCHAR(256)   ENCODE lzo
	,opposition_personal_funds NUMERIC(20,9)   ENCODE az64
	,pages INTEGER   ENCODE az64
	,party VARCHAR(256)   ENCODE lzo
	,pdf_url VARCHAR(256)   ENCODE lzo
	,previous_file_number INTEGER   ENCODE az64
	,primary_general_indicator VARCHAR(256)   ENCODE lzo
	,receipt_date DATE   ENCODE az64
	,report_type VARCHAR(256)   ENCODE lzo
	,report_type_full VARCHAR(256)   ENCODE lzo
	,report_year INTEGER   ENCODE az64
	,request_type VARCHAR(256)   ENCODE lzo
	,senate_personal_funds NUMERIC(20,9)   ENCODE az64
	,state VARCHAR(256)   ENCODE lzo
	,sub_id VARCHAR(256)   ENCODE lzo
	,total_communication_cost NUMERIC(20,9)   ENCODE az64
	,total_disbursements NUMERIC(20,9)   ENCODE az64
	,total_independent_expenditures NUMERIC(20,9)   ENCODE az64
	,total_individual_contributions NUMERIC(20,9)   ENCODE az64
	,total_receipts NUMERIC(20,9)   ENCODE az64
	,treasurer_name VARCHAR(256)   ENCODE lzo
	,update_date DATE   ENCODE az64
	,additional_bank_names VARCHAR(256)   ENCODE lzo
	,bank_depository_city VARCHAR(256)   ENCODE lzo
	,bank_depository_name VARCHAR(256)   ENCODE lzo
	,bank_depository_state VARCHAR(256)   ENCODE lzo
	,bank_depository_street_1 VARCHAR(256)   ENCODE lzo
	,bank_depository_street_2 VARCHAR(256)   ENCODE lzo
	,bank_depository_zip VARCHAR(256)   ENCODE lzo
	,PRIMARY KEY (fec_file_id)
)
DISTSTYLE AUTO
 DISTKEY (fec_file_id)
;
ALTER TABLE fec.filings owner to rhythmic;

-- Table Triggers

create constraint trigger "RI_ConstraintTrigger_3330405" after
insert
    or
update
    on
    fec.filings
from
    fec.candidate_detail not deferrable initially immediate for each row execute procedure "RI_FKey_check_ins"('filings_candidate_id_fkey',
    'filings',
    'candidate_detail',
    'UNSPECIFIED',
    'candidate_id',
    'candidate_id');
create constraint trigger "RI_ConstraintTrigger_3330409" after
insert
    or
update
    on
    fec.filings
from
    fec.committee_detail not deferrable initially immediate for each row execute procedure "RI_FKey_check_ins"('filings_committee_id_fkey',
    'filings',
    'committee_detail',
    'UNSPECIFIED',
    'committee_id',
    'committee_id');
create constraint trigger "RI_ConstraintTrigger_3889852" after
delete
    on
    fec.filings
from
    fec.filing_amendment_chain_2 not deferrable initially immediate for each row execute procedure "RI_FKey_noaction_del"('filing_amendment_chain_2_fec_file_id_fkey',
    'filing_amendment_chain_2',
    'filings',
    'UNSPECIFIED',
    'fec_file_id',
    'fec_file_id');
create constraint trigger "RI_ConstraintTrigger_3889853" after
update
    on
    fec.filings
from
    fec.filing_amendment_chain_2 not deferrable initially immediate for each row execute procedure "RI_FKey_noaction_upd"('filing_amendment_chain_2_fec_file_id_fkey',
    'filing_amendment_chain_2',
    'filings',
    'UNSPECIFIED',
    'fec_file_id',
    'fec_file_id');
create constraint trigger "RI_ConstraintTrigger_3893360" after
delete
    on
    fec.filings
from
    fec.filing_amendment_chain not deferrable initially immediate for each row execute procedure "RI_FKey_noaction_del"('filing_amendment_chain_fec_file_id_fkey',
    'filing_amendment_chain',
    'filings',
    'UNSPECIFIED',
    'fec_file_id',
    'fec_file_id');
create constraint trigger "RI_ConstraintTrigger_3893361" after
update
    on
    fec.filings
from
    fec.filing_amendment_chain not deferrable initially immediate for each row execute procedure "RI_FKey_noaction_upd"('filing_amendment_chain_fec_file_id_fkey',
    'filing_amendment_chain',
    'filings',
    'UNSPECIFIED',
    'fec_file_id',
    'fec_file_id');
