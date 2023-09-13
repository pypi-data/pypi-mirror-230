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

from rttbackend.defines import GET, POST, REFRESH_SYMBOL_GAINERS_LOSERS, FMP_GAINERS, FMP_LOSERS
from rttbackend.exchange import RestExchange

LOG = logging.getLogger('feedhandler')


class FmpRestMixin(RestExchange):
    api = "https://financialmodelingprep.com/"

    def _request(self, method: str, endpoint: str, auth: bool = False, payload={}, api=None):
        query_string = urlencode(payload)

        if auth:
            if query_string:
                query_string = '{}&apikey={}'.format(
                    query_string, self.key_id)
            else:
                query_string = 'apikey={}'.format(self.key_id)

        if not api:
            api = self.api

        url = f'{api}{endpoint}?{query_string}'

        if method == GET:
            return self.http_sync.read(address=url, isCache=True)
        elif method == POST:
            return self.http_sync.write(address=url, data=None)

    def refresh_symbol_gainers_losers(self):
        return [FMP_GAINERS, FMP_LOSERS]

    def gainers(self):
        return self._request(GET, 'api/v3/stock_market/gainers', auth=True)

    def losers(self):
        return self._request(GET, 'api/v3/stock_market/losers', auth=True)
