#!/bin/env python3
"""
database_schema:
- schema objects for db
"""

from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# ORM stuff
Base = declarative_base()
metadata = Base.metadata

class CommitteeCandidate(Base):
    __tablename__ = 'committeecandidates'
    __table_args__ = {'schema': 'fec', 'comment': 'Linking table to connect CommitteeDetail to CandidateDetail'}

    committee_candidate_id = Column(Integer, primary_key=True)
    committee_id = Column(String(8))
    candidate_id = Column(String(10))


class CommitteeDetail(Base):
    __tablename__ = 'committeedetail'
    __table_args__ = {'schema': 'fec'}

    committee_id = Column(String(10), primary_key=True)
    affiliated_committee_name = Column(String(100))
    committee_candidate_id = Column(Integer)
    city = Column(String(50))
    committee_type = Column(String(1), nullable=False)
    committee_type_full = Column(String(50))
    custodian_city = Column(String(50))
    custodian_name_1 = Column(String(50))
    custodian_name_2 = Column(String(50))
    custodian_name_full = Column(String(100))
    custodian_name_middle = Column(String(50))
    custodian_name_prefix = Column(String(50))
    custodian_name_suffix = Column(String(50))
    custodian_name_title = Column(String(50))
    custodian_phone = Column(String(15))
    custodian_state = Column(String(2))
    custodian_street_1 = Column(String(50))
    custodian_street_2 = Column(String(50))
    custodian_zip = Column(String(9))
    cycles = Column(String(200))
    designation = Column(String(1))
    designation_full = Column(String(25))
    email = Column(String(50))
    fax = Column(String(10))
    filing_frequency = Column(String(1))
    first_file_date = Column(Date)
    form_type = Column(String(3))
    last_file_date = Column(Date)
    last_updated = Column(DateTime, nullable=False)
    leadership_pac = Column(String(50))
    lobbyist_registrant_pac = Column(String(1))
    committee_name = Column(String(100))
    organization_type = Column(String(1))
    organization_type_full = Column(String(100))
    party = Column(String(3))
    party_full = Column(String(50))
    party_type = Column(String(3))
    party_type_full = Column(String(15))
    state = Column(String(2))
    state_full = Column(String(50))
    street_1 = Column(String(50))
    street_2 = Column(String(50))
    treasurer_city = Column(String(50))
    treasurer_name = Column(String(100))
    treasurer_name_1 = Column(String(50))
    treasurer_name_2 = Column(String(50))
    treasurer_name_middle = Column(String(50))
    treasurer_name_prefix = Column(String(50))
    treasurer_name_suffix = Column(String(50))
    treasurer_name_title = Column(String(50))
    treasurer_phone = Column(String(15))
    treasurer_state = Column(String(50))
    treasurer_street_1 = Column(String(50))
    treasurer_street_2 = Column(String(50))
    treasurer_zip = Column(String(9))
    website = Column(String(50))
    zip = Column(String(9))
