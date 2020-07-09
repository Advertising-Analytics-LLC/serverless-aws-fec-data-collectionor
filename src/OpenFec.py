#!/bin/env python3
"""
"""

import json
import requests
import logging
from requests import Response
from time import sleep
from typing import Generator


logger = logging.getLogger(__name__)

class OpenFec:
    """Lightweight wrapper over the openFEC api - https://api.open.fec.gov/developers/
    """
    def __init__(self, api_key: str, base_url='https://api.open.fec.gov/v1'):
        self.api_key = api_key
        self.api_arg = '?api_key=' + api_key
        self.base_url = base_url
        self.throttle = 0.5 # seconds to wait between requests

    def _get_route(self, route: str) -> str:
        """internal method to get fully-formed route

        Args:
            route (str): route, eg "/committees/"

        Returns:
            str: fully-formed route, eg https://api.open.fec.gov/v1/committees/?api_key=<API_KEY>
        """
        url = self.base_url + route + self.api_arg
        return url

    def _over_rate_limit(self, response: Response) -> bool:
        """returns true if response has OVER_RATE_LIMIT error

        Args:
            response (Response): Response from requests library

        Returns:
            bool: is request OVER_RATE_LIMIT
        """
        if response.status_code == 429:
            return True
        return False

    def _get_request(self, url: str, payload: dict) -> Response:
        """light wrapper over requests.get

        Args:
            url (str): url to get
            payload (dict): params payload

        Returns:
            Response: Reponse object
        """
        response = requests.get(url, params=payload)
        if self._over_rate_limit(response):
            sleep(self.throttle)
            response =self._get_request(url, payload)
        return response

    def get_committees(self, payload: dict) -> json:
        """get response from committee API

        Args:
            payload (dict): request params object

        Returns:
            json: response as json object, has this structure:
                    {
                      "api_version": "1.0",
                      "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "count": 0,
                        "pages": 0
                      },
                      "results": []
                    }
        """
        route = '/committees/'
        url = self._get_route(route)
        response = self._get_request(url, payload)
        return response.json()

    def get_committees_paginator(self, payload: dict) -> Generator:
        """paginator for committees endpoint

        Args:
            payload (dict): request params

        Yields:
            Generator: python Generator object to iteratate over committee responses
        """
        first_response = self.get_committees(payload)
        yield first_response
        num_pages = first_response['pagination']['pages']
        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = self.get_committees(payload)
            yield next_page
