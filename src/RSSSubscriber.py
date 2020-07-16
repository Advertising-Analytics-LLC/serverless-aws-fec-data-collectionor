#!/bin/env python3
"""RSSSubscriber
- Polls FEC RSS feed for new filings
    - https://efilingapps.fec.gov/rss/display?input
    - F3/F3P/F3X RSS feeds
- Sends committee_id to SNS
"""

import logging
import requests
from requests import Response
import xml.etree.ElementTree as ET


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
            presidential: 'F3P',
            congressional: 'F3',
            pac_and_party: 'F3X'
        }

    def get_rss_by_type(filing_type: str, payload: dict) -> Response:
        """Given a request type it will return that RSS as a requests.Response

        Args:
            filing_type (str): (see self.filings_of_interest)
            payload (dict): request params object

        Returns:
            Response: requests.Response containing RSS
        """
        url = self.base_url + self.query_param + filing_type
        logger.debug(f'GET {url}')
        response = requests.get(url, payload)
        logger.debug(f'status_code: {response.status_code}')
        return response

    def get_items_from_rss(filing_response: Response) -> List[dict]:
        """takes in requests.Response, gets xml, parses xml

        Args:
            filing_response (Response): requests.Response object

        Returns:
            List[dict]: The RSS items as a list of dictionaries
        """
        pass


# handler for aws lambda
def lambdaHandler(event: dict, context: object):
    """lambdaHandler

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    logger.debug('hello world')
