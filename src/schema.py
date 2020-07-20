#!/bin/env python3
"""
Schema holds the database objects as we can use them in code
"""

from collections import OrderedDict
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from src import logger, JSONType
from typing import Union


def parse_value(value: Union[str, int]) -> Union[str, int]:
    """parses values so that sql can put them into redshift

    Args:
        value (Union[str, int]): whatever you're going to insert

    Returns:
        Union[str, int]: whatever, as it can be inserted
    """
    if value is None:
        return ''
    return str(value)


def get_committeecandidates_by_id(committee_id: str, candidate_id: str) -> SQL:
    query = SQL('SELECT * FROM fec.committeecandidates WHERE committee_id = {committee_id} AND candidate_id = {candidate_id}')\
        .format(committee_id=Literal(parse_value(committee_id)), candidate_id=Literal(parse_value(candidate_id)))
    return query


def get_committeecandidates_insert_statement(committee_id: str, candidate_id: str) -> SQL:
    """returns SQL query object to insert committeecandidates record

    Args:
        committee_id (str): ID of committee
        candidate_id (str): ID of candidate

    Returns:
        SQL: insert statement as SQL object
    """
    query = sql.SQL('''
    INSERT INTO fec.committeecandidates(committee_id, candidate_id)
    VALUES ({committee_id}, {candidate_id})
    ''').format(committee_id=Literal(committee_id), candidate_id=Literal(candidate_id))
    return query


def get_committeedetail_by_id(committee_id: str) -> SQL:
    query = sql.SQL('SELECT * FROM fec.committeedetail WHERE committee_id = {committee_id}')\
        .format(committee_id=Literal(parse_value(committee_id)))
    return query


def get_committeedetail_insert_statement(
        committee_id: str,
        committee_type: str,
        affiliated_committee_name='',
        city='',
        committee_name='',
        committee_type_full='',
        custodian_city='',
        custodian_name_1='',
        custodian_name_2='',
        custodian_name_full='',
        custodian_name_middle='',
        custodian_name_prefix='',
        custodian_name_suffix='',
        custodian_name_title='',
        custodian_phone='',
        custodian_state='',
        custodian_street_1='',
        custodian_street_2='',
        custodian_zip='',
        cycles='',
        designation='',
        designation_full='',
        email='',
        fax='',
        filing_frequency='',
        first_file_date='',
        form_type='',
        last_file_date='',
        last_updated='',
        leadership_pac='',
        lobbyist_registrant_pac='',
        organization_type='',
        organization_type_full='',
        party='',
        party_full='',
        party_type='',
        party_type_full='',
        state='',
        state_full='',
        street_1='',
        street_2='',
        treasurer_city='',
        treasurer_name='',
        treasurer_name_1='',
        treasurer_name_2='',
        treasurer_name_middle='',
        treasurer_name_prefix='',
        treasurer_name_suffix='',
        treasurer_name_title='',
        treasurer_phone='',
        treasurer_state='',
        treasurer_street_1='',
        treasurer_street_2='',
        treasurer_zip='',
        website='',
        zip=''):
    """returns insert statement as SQL object for record in committeedetail table

    Args:
        holy cow (str): all the items in a CommitteeDetail

    Returns:
        SQL: insert statement as SQL object
    """
    query = sql.SQL("""
INSERT INTO fec.committeedetail (affiliated_committee_name, city, committee_id, committee_name, committee_type, committee_type_full, custodian_city, custodian_name_1, custodian_name_2, custodian_name_full, custodian_name_middle, custodian_name_prefix, custodian_name_suffix, custodian_name_title, custodian_phone, custodian_state, custodian_street_1, custodian_street_2, custodian_zip, cycles, designation, designation_full, email, fax, filing_frequency, first_file_date, form_type, last_file_date, last_updated, leadership_pac, lobbyist_registrant_pac, organization_type, organization_type_full, party, party_full, party_type, party_type_full, state, state_full, street_1, street_2, treasurer_city, treasurer_name, treasurer_name_1, treasurer_name_2, treasurer_name_middle, treasurer_name_prefix, treasurer_name_suffix, treasurer_name_title, treasurer_phone, treasurer_state, treasurer_street_1, treasurer_street_2, treasurer_zip, website, zip)
VALUES ({affiliated_committee_name}, {city}, {committee_id}, {committee_name}, {committee_type}, {committee_type_full}, {custodian_city}, {custodian_name_1}, {custodian_name_2}, {custodian_name_full}, {custodian_name_middle}, {custodian_name_prefix}, {custodian_name_suffix}, {custodian_name_title}, {custodian_phone}, {custodian_state}, {custodian_street_1}, {custodian_street_2}, {custodian_zip}, {cycles}, {designation}, {designation_full}, {email}, {fax}, {filing_frequency}, {first_file_date}, {form_type}, {last_file_date}, {last_updated}, {leadership_pac}, {lobbyist_registrant_pac}, {organization_type}, {organization_type_full}, {party}, {party_full}, {party_type}, {party_type_full}, {state}, {state_full}, {street_1}, {street_2}, {treasurer_city}, {treasurer_name}, {treasurer_name_1}, {treasurer_name_2}, {treasurer_name_middle}, {treasurer_name_prefix}, {treasurer_name_suffix}, {treasurer_name_title}, {treasurer_phone}, {treasurer_state}, {treasurer_street_1}, {treasurer_street_2}, {treasurer_zip}, {website}, {zip})
""").format(
        affiliated_committee_name=Literal(
            parse_value(affiliated_committee_name)),
        city=Literal(parse_value(city)),
        committee_id=Literal(parse_value(committee_id)),
        committee_name=Literal(parse_value(committee_name)),
        committee_type=Literal(parse_value(committee_type)),
        committee_type_full=Literal(parse_value(committee_type_full)),
        custodian_city=Literal(parse_value(custodian_city)),
        custodian_name_1=Literal(parse_value(custodian_name_1)),
        custodian_name_2=Literal(parse_value(custodian_name_2)),
        custodian_name_full=Literal(parse_value(custodian_name_full)),
        custodian_name_middle=Literal(parse_value(custodian_name_middle)),
        custodian_name_prefix=Literal(parse_value(custodian_name_prefix)),
        custodian_name_suffix=Literal(parse_value(custodian_name_suffix)),
        custodian_name_title=Literal(parse_value(custodian_name_title)),
        custodian_phone=Literal(parse_value(custodian_phone)),
        custodian_state=Literal(parse_value(custodian_state)),
        custodian_street_1=Literal(parse_value(custodian_street_1)),
        custodian_street_2=Literal(parse_value(custodian_street_2)),
        custodian_zip=Literal(parse_value(custodian_zip)),
        cycles=Literal(parse_value(cycles)),
        designation=Literal(parse_value(designation)),
        designation_full=Literal(parse_value(designation_full)),
        email=Literal(parse_value(email)),
        fax=Literal(parse_value(fax)),
        filing_frequency=Literal(parse_value(filing_frequency)),
        first_file_date=Literal(parse_value(first_file_date)),
        form_type=Literal(parse_value(form_type)),
        last_file_date=Literal(parse_value(last_file_date)),
        last_updated=Literal(parse_value(last_updated)),
        leadership_pac=Literal(parse_value(leadership_pac)),
        lobbyist_registrant_pac=Literal(parse_value(lobbyist_registrant_pac)),
        organization_type=Literal(parse_value(organization_type)),
        organization_type_full=Literal(parse_value(organization_type_full)),
        party=Literal(parse_value(party)),
        party_full=Literal(parse_value(party_full)),
        party_type=Literal(parse_value(party_type)),
        party_type_full=Literal(parse_value(party_type_full)),
        state=Literal(parse_value(state)),
        state_full=Literal(parse_value(state_full)),
        street_1=Literal(parse_value(street_1)),
        street_2=Literal(parse_value(street_2)),
        treasurer_city=Literal(parse_value(treasurer_city)),
        treasurer_name=Literal(parse_value(treasurer_name)),
        treasurer_name_1=Literal(parse_value(treasurer_name_1)),
        treasurer_name_2=Literal(parse_value(treasurer_name_2)),
        treasurer_name_middle=Literal(parse_value(treasurer_name_middle)),
        treasurer_name_prefix=Literal(parse_value(treasurer_name_prefix)),
        treasurer_name_suffix=Literal(parse_value(treasurer_name_suffix)),
        treasurer_name_title=Literal(parse_value(treasurer_name_title)),
        treasurer_phone=Literal(parse_value(treasurer_phone)),
        treasurer_state=Literal(parse_value(treasurer_state)),
        treasurer_street_1=Literal(parse_value(treasurer_street_1)),
        treasurer_street_2=Literal(parse_value(treasurer_street_2)),
        treasurer_zip=Literal(parse_value(treasurer_zip)),
        website=Literal(parse_value(website)),
        zip=Literal(parse_value(zip)),
    )
    return query


def get_committeedetail_update_statement(
        committee_id: str,
        committee_type: str,
        affiliated_committee_name='',
        city='',
        committee_name='',
        committee_type_full='',
        custodian_city='',
        custodian_name_1='',
        custodian_name_2='',
        custodian_name_full='',
        custodian_name_middle='',
        custodian_name_prefix='',
        custodian_name_suffix='',
        custodian_name_title='',
        custodian_phone='',
        custodian_state='',
        custodian_street_1='',
        custodian_street_2='',
        custodian_zip='',
        cycles='',
        designation='',
        designation_full='',
        email='',
        fax='',
        filing_frequency='',
        first_file_date='',
        form_type='',
        last_file_date='',
        last_updated='',
        leadership_pac='',
        lobbyist_registrant_pac='',
        organization_type='',
        organization_type_full='',
        party='',
        party_full='',
        party_type='',
        party_type_full='',
        state='',
        state_full='',
        street_1='',
        street_2='',
        treasurer_city='',
        treasurer_name='',
        treasurer_name_1='',
        treasurer_name_2='',
        treasurer_name_middle='',
        treasurer_name_prefix='',
        treasurer_name_suffix='',
        treasurer_name_title='',
        treasurer_phone='',
        treasurer_state='',
        treasurer_street_1='',
        treasurer_street_2='',
        treasurer_zip='',
        website='',
        zip=''):
    """returns insert statement as SQL object for record in committeedetail table

    Args:
        holy cow (str): all the items in a CommitteeDetail

    Returns:
        SQL: insert statement as SQL object
    """
    query = sql.SQL("""
UPDATE fec.committeedetail
SET affiliated_committee_name={affiliated_committee_name}, city={city}, committee_name={committee_name}, committee_type={committee_type}, committee_type_full={committee_type_full}, custodian_city={custodian_city}, custodian_name_1={custodian_name_1}, custodian_name_2={custodian_name_2}, custodian_name_full={custodian_name_full}, custodian_name_middle={custodian_name_middle}, custodian_name_prefix={custodian_name_prefix}, custodian_name_suffix={custodian_name_suffix}, custodian_name_title={custodian_name_title}, custodian_phone={custodian_phone}, custodian_state={custodian_state}, custodian_street_1={custodian_street_1}, custodian_street_2={custodian_street_2}, custodian_zip={custodian_zip}, cycles={cycles}, designation={designation}, designation_full={designation_full}, email={email}, fax={fax}, filing_frequency={filing_frequency}, first_file_date={first_file_date}, form_type={form_type}, last_file_date={last_file_date}, last_updated={last_updated}, leadership_pac={leadership_pac}, lobbyist_registrant_pac={lobbyist_registrant_pac}, organization_type={organization_type}, organization_type_full={organization_type_full}, party={party}, party_full={party_full}, party_type={party_type}, party_type_full={party_type_full}, state={state}, state_full={state_full}, street_1={street_1}, street_2={street_2}, treasurer_city={treasurer_city}, treasurer_name={treasurer_name}, treasurer_name_1={treasurer_name_1}, treasurer_name_2={treasurer_name_2}, treasurer_name_middle={treasurer_name_middle}, treasurer_name_prefix={treasurer_name_prefix}, treasurer_name_suffix={treasurer_name_suffix}, treasurer_name_title={treasurer_name_title}, treasurer_phone={treasurer_phone}, treasurer_state={treasurer_state}, treasurer_street_1={treasurer_street_1}, treasurer_street_2={treasurer_street_2}, treasurer_zip={treasurer_zip}, website={website}, zip={zip}
WHERE committee_id={committee_id}
""").format(
        affiliated_committee_name=Literal(
            parse_value(affiliated_committee_name)),
        city=Literal(parse_value(city)),
        committee_id=Literal(parse_value(committee_id)),
        committee_name=Literal(parse_value(committee_name)),
        committee_type=Literal(parse_value(committee_type)),
        committee_type_full=Literal(parse_value(committee_type_full)),
        custodian_city=Literal(parse_value(custodian_city)),
        custodian_name_1=Literal(parse_value(custodian_name_1)),
        custodian_name_2=Literal(parse_value(custodian_name_2)),
        custodian_name_full=Literal(parse_value(custodian_name_full)),
        custodian_name_middle=Literal(parse_value(custodian_name_middle)),
        custodian_name_prefix=Literal(parse_value(custodian_name_prefix)),
        custodian_name_suffix=Literal(parse_value(custodian_name_suffix)),
        custodian_name_title=Literal(parse_value(custodian_name_title)),
        custodian_phone=Literal(parse_value(custodian_phone)),
        custodian_state=Literal(parse_value(custodian_state)),
        custodian_street_1=Literal(parse_value(custodian_street_1)),
        custodian_street_2=Literal(parse_value(custodian_street_2)),
        custodian_zip=Literal(parse_value(custodian_zip)),
        cycles=Literal(parse_value(cycles)),
        designation=Literal(parse_value(designation)),
        designation_full=Literal(parse_value(designation_full)),
        email=Literal(parse_value(email)),
        fax=Literal(parse_value(fax)),
        filing_frequency=Literal(parse_value(filing_frequency)),
        first_file_date=Literal(parse_value(first_file_date)),
        form_type=Literal(parse_value(form_type)),
        last_file_date=Literal(parse_value(last_file_date)),
        last_updated=Literal(parse_value(last_updated)),
        leadership_pac=Literal(parse_value(leadership_pac)),
        lobbyist_registrant_pac=Literal(parse_value(lobbyist_registrant_pac)),
        organization_type=Literal(parse_value(organization_type)),
        organization_type_full=Literal(parse_value(organization_type_full)),
        party=Literal(parse_value(party)),
        party_full=Literal(parse_value(party_full)),
        party_type=Literal(parse_value(party_type)),
        party_type_full=Literal(parse_value(party_type_full)),
        state=Literal(parse_value(state)),
        state_full=Literal(parse_value(state_full)),
        street_1=Literal(parse_value(street_1)),
        street_2=Literal(parse_value(street_2)),
        treasurer_city=Literal(parse_value(treasurer_city)),
        treasurer_name=Literal(parse_value(treasurer_name)),
        treasurer_name_1=Literal(parse_value(treasurer_name_1)),
        treasurer_name_2=Literal(parse_value(treasurer_name_2)),
        treasurer_name_middle=Literal(parse_value(treasurer_name_middle)),
        treasurer_name_prefix=Literal(parse_value(treasurer_name_prefix)),
        treasurer_name_suffix=Literal(parse_value(treasurer_name_suffix)),
        treasurer_name_title=Literal(parse_value(treasurer_name_title)),
        treasurer_phone=Literal(parse_value(treasurer_phone)),
        treasurer_state=Literal(parse_value(treasurer_state)),
        treasurer_street_1=Literal(parse_value(treasurer_street_1)),
        treasurer_street_2=Literal(parse_value(treasurer_street_2)),
        treasurer_zip=Literal(parse_value(treasurer_zip)),
        website=Literal(parse_value(website)),
        zip=Literal(parse_value(zip)),
    )
    return query

# fec filings


def fec_file_exists(fec_file_id: str) -> SQL:
    query = sql.SQL('SELECT * FROM fec.filings WHERE fec_file_id={fec_file_id}')\
        .format(fec_file_id=Literal(fec_file_id))
    return query


def insert_fec_filing(filing: JSONType) -> SQL:
    values = OrderedDict(sorted(filing.items()))
    query = sql.SQL('''
    INSERT INTO fec.filings VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
    ''').format(*[Literal(val) for key, val in values.items()])
    return query


def update_fec_filing(filing: JSONType) -> SQL:
    fec_file_id = filing.pop('fec_file_id')
    values = OrderedDict(sorted(filing.items()))
    query_string = 'UPDATE fec.filings SET ' \
        + ', '.join([f' {key}={{}}' for key, val in values.items()])\
        + ' WHERE fec_file_id={}'
    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()], Literal(fec_file_id))
    return query


def amendment_chain_exists(fec_file_id: str, amendment_id: str) -> SQL:
    query = sql.SQL('SELECT * FROM fec.filing_amendment_chain WHERE fec_file_id={} AND amendment_id={}')\
        .format(Literal(fec_file_id), Literal(amendment_id))
    return query


def insert_amendment_chain(fec_file_id: str, amendment_id: str, amendment_number: int) -> SQL:
    query = sql.SQL('INSERT INTO fec.filing_amendment_chain(fec_file_id, amendment_id, amendment_number) VALUES ({}, {}, {})')\
        .format(Literal(fec_file_id), Literal(amendment_id), Literal(amendment_number))
    return query


# comittee totals

def committee_total_exists(committee_id: str, cycle: int) -> SQL:
    query = sql.SQL('SELECT * FROM fec.committee_totals WHERE fec_file_id={committee_id} AND cycle={cycle}')\
        .format(committee_id=Literal(committee_id), cycle=Literal(cycle))
    return query


def insert_committee_total(committee_total: JSONType) -> SQL:
    values = OrderedDict(sorted(filing.items()))
    query = sql.SQL('''
    INSERT INTO fec.committee_totals
    VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
    ''').format(*[Literal(val) for key, val in values.items()])
    return query

def update_committee_total(committee_total: JSONType) -> SQL:
    committee_id = committee_total.pop('committee_id')
    cycle = committee_total.pop('cycle')

    values = OrderedDict(sorted(filing.items()))
    query_string = 'UPDATE fec.committee_totals SET ' \
        + ', '.join([f' {key}={{}}' for key, val in values.items()])\
        + ' WHERE committee_id={}'\
        + ' AND cycle={}'
    query = sql.SQL(query_string)\
        .format(*[Literal(val) for key, val in values.items()], Literal(committee_id), Literal(cycle))

    return query
