#!/bin/env python3
"""
Schema holds the database objects as we can use them in code
"""
import logging
from psycopg2 import sql
from psycopg2.sql import SQL, Literal
from typing import Union


# logging
logger = logging.getLogger(__name__)


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
    logger.debug(query)
    return query
