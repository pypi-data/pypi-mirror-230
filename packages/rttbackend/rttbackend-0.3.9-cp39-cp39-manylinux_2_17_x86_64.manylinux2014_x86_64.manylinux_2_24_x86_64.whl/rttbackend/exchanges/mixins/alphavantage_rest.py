'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
import asyncio
from decimal import Decimal
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode


from yapic import json

from rttbackend.defines import GET, POST, REFRESH_SYMBOL_LOOKUP, AV_SYMBOL_SEARCH, AV_OVERVIEW, REFRESH_SYMBOL, AV_GAINERS_LOSERS
from rttbackend.exchange import RestExchange

LOG = logging.getLogger('feedhandler')


class AlphaVantageRestMixin(RestExchange):
    api = "https://www.alphavantage.co/"

    def _request(self, method: str, endpoint: str, auth: bool = False, payload={}, api=None):
        query_string = urlencode(payload)

        if auth:
            if query_string:
                query_string = '{}&apikey={}'.format(query_string, self.key_id)
            else:
                query_string = 'apikey={}'.format(self.key_id)

        if not api:
            api = self.api

        url = f'{api}{endpoint}?{query_string}'

        if method == GET:
            return self.http_sync.read(address=url, isCache=True, retry_message=self.retry_message)
        elif method == POST:
            return self.http_sync.write(address=url, data=None)

    def retry_message(self):
        return
        {
            'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency.'
        }

    def refresh_symbol_lookup(self):
        return [AV_SYMBOL_SEARCH, AV_OVERVIEW]

    def symbol_search(self, symbol: str):
        return self._request(GET, 'query', auth=True, payload={'function': 'SYMBOL_SEARCH', 'keywords': symbol})

    def overview(self, symbol: str):
        return self._request(GET, 'query', auth=True, payload={'function': 'OVERVIEW', 'symbol': symbol})

    def refresh_symbol_gainers_losers(self):
        return [AV_GAINERS_LOSERS]

    def gainers_losers(self):
        return self._request(GET, 'query', auth=True, payload={'function': 'TOP_GAINERS_LOSERS'})
