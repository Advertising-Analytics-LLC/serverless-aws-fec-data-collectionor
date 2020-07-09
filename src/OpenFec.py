#!/bin/env python3
"""
"""

import json
import requests
from requests import Response



class OpenFec:
    """Lightweight wrapper over the openFEC api - https://api.open.fec.gov/developers/
    """
    def __init__(self, api_key: str, base_url='https://api.open.fec.gov/v1'):
        self.api_key = api_key
        self.api_arg = '?api_key=' + api_key
        self.base_url = base_url

    def _get_route(self, route: str) -> str:
        """internal method to get fully-formed route

        Args:
            route (str): route, eg "/committees/"

        Returns:
            str: fully-formed route, eg https://api.open.fec.gov/v1/committees/?api_key=<API_KEY>
        """
        url = self.base_url + route + self.api_arg
        return url

    def get_committees(self, payload: dict) -> json:
        route = '/committees/'
        url = self._get_route(route)
        response = requests.get(url, params=payload)
        return response.json()

    def get_committees_paginator(self, payload: dict):
        first_response = self.get_committees(payload)
        print('first_response')
        print(first_response)
        yield first_response
        num_pages = first_response['pagination']['pages']
        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = self.get_committees(payload)
            print('next_page')
            print(next_page)
            yield next_page
