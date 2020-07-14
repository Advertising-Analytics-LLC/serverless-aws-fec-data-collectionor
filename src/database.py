#!/bin/env python3
"""
Database:
- helper to work with database (redshift)
"""

import logging
from src.database_schema import CommitteeDetail, CommitteeCandidate
from src.secrets import get_param_value_by_name
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Tuple


# logging
logger = logging.getLogger(__name__)

# SSM VARS
DATABASE = get_param_value_by_name('/global/fec-schema/database')
HOSTNAME = get_param_value_by_name('/global/fec-schema/hostname')
PASSWORD = get_param_value_by_name('/global/fec-schema/password')
PORT = get_param_value_by_name('/global/fec-schema/port')
USERNAME = get_param_value_by_name('/global/fec-schema/username')

class Database:
    """redshift wrapper
    """
    def __init__(self):
        """creates connection to redshift database and performs operations
            Gets connection variables from SSM
        """
        self._connection_string = f'postgresql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
        self._engine = create_engine(self._connection_string)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()

    def _transform_committee_detail(self, committee_detail: any) -> CommitteeDetail:
        """[summary]

        Args:
            committee_detail (any): [description]
        """
        committee_id = committee_detail['committee_id']
        # get canidate ids
        candidate_ids = committee_detail.pop('candidate_ids')
        for candidate_id in candidate_ids:
            new_element = CommitteeCandidate(committee_id=committee_id, candidate_id=candidate_id)
            ret = self._session.add(new_element)
            logger.debug(ret)

        ret = self._session.commit()
        logger.debug(ret)
        # date this update
        committee_detail['last_updated'] = "'now'"
        # rename key
        committee_detail['committee_name'] = committee_detail.pop('name')
        # convert cycles list seperated by ~
        committee_detail['cycles'] = '~'.join(str(cycle) for cycle in committee_detail['cycles'])
        # construct row object
        committeeDetail = CommitteeDetail(**committee_detail)
        return committeeDetail

    def write_committee_detail(self, committee_detail: any):
        """[summary]

        Args:
            committee_detail (JSON): [description]
        """
        # try:
        committeeDetail = self._transform_committee_detail(committee_detail)

        ret = self._session.add(committeeDetail)
        logger.debug(ret)
        ret = self._session.commit()
        logger.debug(ret)
        # except:
            # logger.error(f'rolling back committee_id {committee_id}')
            # self._session.rollback()
