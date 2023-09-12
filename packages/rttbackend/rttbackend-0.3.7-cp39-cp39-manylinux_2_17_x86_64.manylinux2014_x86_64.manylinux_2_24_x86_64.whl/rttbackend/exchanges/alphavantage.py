'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''

from rttbackend.defines import *
from rttbackend.exchange import Exchange
from rttbackend.connection import RestEndpoint, Routes
from rttbackend.symbols import Symbol
from rttbackend.exchanges.mixins.alphavantage_rest import AlphaVantageRestMixin
from rttbackend.exceptions import UnsupportedSymbol
from rttbackend.types import RefreshSymbols, RefreshSymbolLookup, RefreshSymbolGainersLosers


from typing import Dict, List, Tuple, Union
from decimal import Decimal
import csv
from time import time
from yapic import json

from prefect import flow, task


class AlphaVantage(Exchange, AlphaVantageRestMixin):
    id = ALPHAVANTAGE
    rest_endpoints = [RestEndpoint(
        'https://www.alphavantage.co/', routes=Routes(['query?function=LISTING_STATUS']))]
    key_seperator = ','

    @classmethod
    def symbol_replace(self, symbol):
        return symbol.replace('-', '/').replace('+', '')

    @classmethod
    def _parse_symbol_data(cls, data: dict) -> Tuple[Dict, Dict]:

        ret = {}

        for i in csv.reader(data.splitlines(), delimiter=','):
            type = i[3]
            if type == 'Stock':
                symbol = i[0]

                symbol = cls.symbol_replace(symbol)

                s = Symbol(symbol, 'USD')
                ret[s.normalized] = str(symbol)

        return ret

    @classmethod
    def _symbol_endpoint_prepare(cls, ep: RestEndpoint, key_id) -> Union[List[str], str]:
        """
        override if a specific exchange needs to do something first, like query an API
        to get a list of currencies, that are then used to build the list of symbol endpoints
        """
        return [ep + '&apikey=' + key_id for ep in ep.route('instruments')]

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

    def _symbol_search(self, msg, ts):
        data = []

        for i in msg['bestMatches']:

            try:
                base, quote = self.exchange_symbol_to_std_symbol(
                    self.symbol_replace(i['1. symbol'])).split('-')

                data.append(RefreshSymbolLookup(
                    exchange=self.id,
                    base_symbol=base,
                    quote_symbol=quote,
                    name=i['2. name'],
                    type=i['3. type'],
                    region=i['4. region'],
                    market_open=i['5. marketOpen'],
                    market_close=i['6. marketClose'],
                    time_zone=i['7. timezone'],

                    timestamp=ts,
                    raw=i
                ))

            except Exception:
                pass

        return data

    def _overview(self, msg, ts):
        data = []

        try:
            base, quote = self.exchange_symbol_to_std_symbol(
                self.symbol_replace(msg['Symbol'])).split('-')

            data.append(RefreshSymbolLookup(
                        exchange=self.id,
                        base_symbol=base,
                        quote_symbol=quote,

                        name=msg['Name'],
                        type=msg['AssetType'],
                        description=msg['Description'].replace("'", ""),
                        symbol_exchange=msg['Exchange'],
                        cik=msg['CIK'],

                        country=msg['Country'],
                        sector=msg['Sector'],
                        industry=msg['Industry'],
                        address=msg['Address'],

                        timestamp=ts,
                        raw=msg
                        ))
            return data
        except Exception:
            pass

    def _gainers_losers(self, msg, ts):
        data = []

        for i in msg['top_gainers']:
            try:
                base, quote = self.exchange_symbol_to_std_symbol(
                    self.symbol_replace(i['ticker'])).split('-')

                data.append(RefreshSymbolGainersLosers(
                            exchange=self.id,
                            base_symbol=base,
                            quote_symbol=quote,
                            movement=GAINERS,
                            price=abs(i['price']),
                            change_amount=abs(i['change_amount']),
                            change_percentage=abs(i['change_percentage']).replace(
                                '%', ''),
                            volume=i['volume'],

                            timestamp=ts,
                            raw=i
                            ))
            except Exception:
                pass

        for i in msg['top_losers']:
            try:
                base, quote = self.exchange_symbol_to_std_symbol(
                    self.symbol_replace(i['ticker'])).split('-')

                data.append(RefreshSymbolGainersLosers(
                            exchange=self.id,
                            base_symbol=base,
                            quote_symbol=quote,
                            movement=LOSERS,
                            price=abs(i['price']),
                            change_amount=abs(i['change_amount']),
                            change_percentage=abs(i['change_percentage']).replace(
                                '%', ''),
                            volume=i['volume'],

                            timestamp=ts,
                            raw=i
                            ))
            except Exception:
                pass

        return data

    def refresh_symbol(self):
        return [AV_SYMBOL]

    def message_handler(self, type, msg, symbol=None):

        try:
            msg = json.loads(msg, parse_float=Decimal)
        except Exception:
            pass

        if type == AV_SYMBOL:
            return self._symbol(msg, time())
        elif type == AV_SYMBOL_SEARCH:
            return self._symbol_search(msg, time())
        elif type == AV_OVERVIEW:
            return self._overview(msg, time())
        elif type == AV_GAINERS_LOSERS:
            return self._gainers_losers(msg, time())

    def __getitem__(self, key):
        if key == REFRESH_SYMBOL:
            return self.refresh_symbol
        elif key == REFRESH_SYMBOL_LOOKUP:
            return self.refresh_symbol_lookup
        elif key == AV_SYMBOL:
            return self.symbol
        elif key == AV_SYMBOL_SEARCH:
            return self.symbol_search
        elif key == AV_OVERVIEW:
            return self.overview
        elif key == REFRESH_SYMBOL_GAINERS_LOSERS:
            return self.refresh_symbol_gainers_losers
        elif key == AV_GAINERS_LOSERS:
            return self.gainers_losers
