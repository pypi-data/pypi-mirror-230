'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''

from rttbackend.defines import FMP, REFRESH_SYMBOL, REFRESH_SYMBOL_PEERS, FMP_SYMBOL, REFRESH_SYMBOL_GAINERS_LOSERS, FMP_GAINERS, FMP_LOSERS, LOSERS, GAINERS
from rttbackend.exchange import Exchange
from rttbackend.connection import RestEndpoint, Routes
from rttbackend.symbols import Symbol
from rttbackend.exchanges.mixins.fmp_rest import FmpRestMixin
from rttbackend.exceptions import UnsupportedSymbol
from rttbackend.types import RefreshSymbols, RefreshSymbolLookup, RefreshSymbolPeers, RefreshSymbolGainersLosers


from typing import Dict, List, Tuple, Union
from decimal import Decimal
import csv
from time import time
from yapic import json

from prefect import flow, task


class Fmp(Exchange, FmpRestMixin):
    id = FMP
    rest_endpoints = [RestEndpoint(
        'https://financialmodelingprep.com/', routes=Routes(['api/v3/stock/list']))]
    key_seperator = ','

    @classmethod
    def symbol_replace(self, symbol):
        return symbol.replace('-', '/')

    @classmethod
    def _parse_symbol_data(cls, data: dict) -> Tuple[Dict, Dict]:

        ret = {}

        for i in data:
            type = i['type']
            exchangeShortName = i['exchangeShortName']
            if type == 'stock':
                if exchangeShortName in ('NYSE', 'NASDAQ'):
                    symbol = i['symbol']
                    currency = 'USD'

                    symbol = cls.symbol_replace(symbol)

                    s = Symbol(symbol, currency)

                    ret[s.normalized] = str(symbol)
        return ret

    @classmethod
    def _symbol_endpoint_prepare(cls, ep: RestEndpoint, key_id) -> Union[List[str], str]:
        """
        override if a specific exchange needs to do something first, like query an API
        to get a list of currencies, that are then used to build the list of symbol endpoints
        """

        return [ep + '?apikey=' + key_id for ep in ep.route('instruments')]

    def symbol(self):
        data = []
        for j in self.symbols():
            base, quote = j.split('-')
            data.append({'base': base, 'quote': quote, 'symbol': j})

        return json.dumps(data)

    def refresh_symbol(self):
        return [FMP_SYMBOL]

    def _symbol(self, msg, ts):
        data = []
        for j in msg:
            data.append(RefreshSymbols(
                self.id, j['symbol'], j['base'], j['quote'], ts, raw=j))
        return data

    def _gainers(self, msg, ts):
        data = []
        for i in msg:
            try:
                base, quote = self.exchange_symbol_to_std_symbol(
                    self.symbol_replace(i['symbol'])).split('-')

                data.append(RefreshSymbolGainersLosers(
                            exchange=self.id,
                            base_symbol=base,
                            quote_symbol=quote,
                            movement=GAINERS,
                            price=abs(i['price']),
                            change_amount=abs(i['change']),
                            change_percentage=abs(i['changesPercentage']),
                            name=i['name'],

                            timestamp=ts,
                            raw=i
                            ))
            except UnsupportedSymbol:
                pass

        return data

    def _losers(self, msg, ts):
        data = []
        for i in msg:
            try:
                base, quote = self.exchange_symbol_to_std_symbol(
                    self.symbol_replace(i['symbol'])).split('-')

                data.append(RefreshSymbolGainersLosers(
                    exchange=self.id,
                    base_symbol=base,
                    quote_symbol=quote,
                    movement=LOSERS,
                    price=abs(i['price']),
                    change_amount=abs(i['change']),
                    change_percentage=abs(i['changesPercentage']),
                    name=i['name'],

                    timestamp=ts,
                    raw=i
                ))
            except UnsupportedSymbol:
                pass

        return data

    def message_handler(self, type, msg, symbol=None):

        msg = json.loads(msg, parse_float=Decimal)

        if type == FMP_SYMBOL:
            return self._symbol(msg, time())
        elif type == FMP_GAINERS:
            return self._gainers(msg, time())
        elif type == FMP_LOSERS:
            return self._losers(msg, time())

    def __getitem__(self, key):
        if key == REFRESH_SYMBOL:
            return self.refresh_symbol
        elif key == FMP_SYMBOL:
            return self.symbol
        elif key == REFRESH_SYMBOL_GAINERS_LOSERS:
            return self.refresh_symbol_gainers_losers
        elif key == FMP_GAINERS:
            return self.gainers
        elif key == FMP_LOSERS:
            return self.losers
