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

from rttbackend.defines import GET, POST, FH_PROFILE, FH_PEERS
from rttbackend.exchange import RestExchange

LOG = logging.getLogger('feedhandler')


class FinnhubRestMixin(RestExchange):
    api = "https://finnhub.io/"

    def _request(self, method: str, endpoint: str, auth: bool = False, payload={}, api=None):
        query_string = urlencode(payload)

        if auth:
            if query_string:
                query_string = '{}&token={}'.format(query_string, self.key_id)
            else:
                query_string = 'token={}'.format(self.key_id)

        if not api:
            api = self.api

        url = f'{api}{endpoint}?{query_string}'

        if method == GET:
            return self.http_sync.read(address=url, isCache=True)
        elif method == POST:
            return self.http_sync.write(address=url, data=None)

    def refresh_symbol_lookup(self):
        return [FH_PROFILE]

    def profile(self, symbol: str):
        return self._request(GET, 'api/v1/stock/profile2', auth=True, payload={'symbol': symbol})

    def refresh_symbol_peers(self):
        return [FH_PEERS]

    def peers(self, symbol: str):
        return self._request(GET, 'api/v1/stock/peers', auth=True, payload={'symbol': symbol})
