#!/bin/env python3
"""RSSSubscriber
- Polls FEC RSS feed for new filings
    - https://efilingapps.fec.gov/rss/display?input
    - F3/F3P/F3X RSS feeds
- Sends committee_id to SNS
"""

import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from requests import Response
from typing import List


# SSM VARS
RSS_SNS_TOPIC_ARN = os.getenv('RSS_SNS_TOPIC_ARN')

# LOGGING
logger = logging.getLogger(__name__)

class EFilingRSSFeed:
    """wrapper for the FEC Electronic Filing RSS Feed
    https://efilingapps.fec.gov/rss/display?input
    """

    def __init__(self):
        """returns self with the basic info we need to start pulling at the RSS feed
        """
        self.base_url = 'https://efilingapps.fec.gov/rss/generate'
        self.query_param = '?preDefinedFilingType='
        self.filings_of_interest = {
            'presidential': 'F3P',
            'congressional': 'F3',
            'pac_and_party': 'F3X'
        }

    def get_rss_by_type(self, filing_type: str, payload={}) -> Response:
        """Given a request type it will return that RSS as a requests.Response
        uses session, adapter to prevent
        `RemoteDisconnected('Remote end closed connection without response`

        Args:
            filing_type (str): (see self.filings_of_interest)
            payload (dict): request params object

        Returns:
            Response: requests.Response containing RSS
        """

        url = self.base_url + self.query_param + filing_type
        logger.debug(f'GET {url}')
        headers = {
            'Accept': '*/*',
            'User-Agent': 'requests'
        }
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        session.mount('https://', adapter)
        response = session.get(url, stream=True, timeout=5, headers=headers)
        logger.debug(f'status_code: {response.status_code}')

        return response

    def parse_rss(self, filing_response: Response) -> List[str]:
        """takes in requests.Response, gets xml, parses xml

        Args:
            filing_response (Response): requests.Response object

        Returns:
            List[dict]: The RSS items as a list of dictionaries
        """
        regex = r'(CommitteeId: )(C[0-9]*)'
        committee_id_list = []
        soup = BeautifulSoup(filing_response.content, 'xml')
        descriptions = soup.find_all('description')
        for desc in descriptions:
            logger.debug(desc.text)
            matches = re.findall(regex, str(desc), re.MULTILINE)
            if len(matches) > 1:
                match = matches[1]
                committee_id_list.append(match)

        return committee_id_list

    def get_items_from_rss_feeds_of_interest(self) -> List[str]:
        items = []
        for key, item in self.filings_of_interest.items():
            rss = self.get_rss_by_type(item)
            rss_items = self.parse_rss(rss)
            items.append(rss_items)
        return items


# handler for aws lambda
def lambdaHandler(event: dict, context: object):
    """lambdaHandler

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    eFilingRSSFeed = EFilingRSSFeed()
    items = eFilingRSSFeed.get_items_from_rss_feeds_of_interest()
