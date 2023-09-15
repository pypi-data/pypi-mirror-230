'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''

from rttbackend.defines import FINNHUB, REFRESH_SYMBOL, REFRESH_SYMBOL_LOOKUP, FH_PROFILE, REFRESH_SYMBOL_PEERS, FH_PEERS, FH_SYMBOL
from rttbackend.exchange import Exchange
from rttbackend.connection import RestEndpoint, Routes
from rttbackend.symbols import Symbol
from rttbackend.exchanges.mixins.finnhub_rest import FinnhubRestMixin
from rttbackend.exceptions import UnsupportedSymbol
from rttbackend.types import RefreshSymbols, RefreshSymbolLookup, RefreshSymbolPeers


from typing import Dict, List, Tuple, Union
from decimal import Decimal
import csv
from time import time
from yapic import json

from prefect import flow, task


class Finnhub(Exchange, FinnhubRestMixin):
    id = FINNHUB
    rest_endpoints = [RestEndpoint(
        'https://finnhub.io/', routes=Routes(['api/v1/stock/symbol?exchange=US']))]
    key_seperator = ','

    @classmethod
    def _parse_symbol_data(cls, data: dict) -> Tuple[Dict, Dict]:

        ret = {}

        for i in data:
            type = i['type']
            if type == 'Common Stock':
                symbol = i['symbol']
                currency = i['currency']

                symbol = symbol.replace('.', '/')

                s = Symbol(symbol, currency)

                ret[s.normalized] = str(symbol)
        return ret

    @classmethod
    def _symbol_endpoint_prepare(cls, ep: RestEndpoint, key_id) -> Union[List[str], str]:
        """
        override if a specific exchange needs to do something first, like query an API
        to get a list of currencies, that are then used to build the list of symbol endpoints
        """
        return [ep + '&token=' + key_id for ep in ep.route('instruments')]

    def symbol(self):
        data = []
        for j in self.symbols():
            base, quote = j.split('-')
            data.append({'base': base, 'quote': quote, 'symbol': j})

        return json.dumps(data)

    def _symbol(self, msg, ts):
        data = []
        for j in msg:
            data.append(RefreshSymbols(
                self.id, j['symbol'], j['base'], j['quote'], ts, raw=j))
        return data

    def _profile(self, msg, ts):
        data = []
        try:
            base, quote = self.exchange_symbol_to_std_symbol(
                msg['ticker']).split('-')

            data.append(RefreshSymbolLookup(
                        exchange=self.id,
                        base_symbol=base,
                        quote_symbol=quote,

                        name=msg['name'],
                        symbol_exchange=msg['exchange'],
                        country=msg['country'],

                        industry=msg['finnhubIndustry'],
                        ipo=str(msg['ipo']),
                        phone=msg['phone'],
                        website=msg['weburl'],

                        logo=msg['logo'],

                        timestamp=ts,
                        raw=msg
                        ))
            return data
        except UnsupportedSymbol:
            pass

    def _peers(self, msg, symbol, ts):
        data = []
        for i in msg:
            try:
                peer, quote = self.exchange_symbol_to_std_symbol(
                    i).split('-')
                data.append(RefreshSymbolPeers(
                    exchange=self.id,
                    base_symbol=symbol,
                    peer_symbol=peer,
                    timestamp=ts,
                    raw=msg
                ))

            except UnsupportedSymbol:
                pass
        return data

    def refresh_symbol(self):
        return [FH_SYMBOL]

    def message_handler(self, type, msg, symbol=None):

        try:
            msg = json.loads(msg, parse_float=Decimal)
        except Exception:
            pass

        if type == FH_SYMBOL:
            return self._symbol(msg, time())
        elif type == FH_PROFILE:
            return self._profile(msg, time())
        elif type == FH_PEERS:
            return self._peers(msg, symbol, time())

    def __getitem__(self, key):
        if key == REFRESH_SYMBOL:
            return self.refresh_symbol
        elif key == REFRESH_SYMBOL_LOOKUP:
            return self.refresh_symbol_lookup
        elif key == FH_SYMBOL:
            return self.symbol
        elif key == FH_PROFILE:
            return self.profile
        elif key == REFRESH_SYMBOL_PEERS:
            return self.refresh_symbol_peers
        elif key == FH_PEERS:
            return self.peers
