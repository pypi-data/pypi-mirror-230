'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
from datetime import datetime as dt, timezone
from typing import Dict, Tuple, Union


class Symbol:
    symbol_sep = '-'

    def __init__(self, base: str, quote: str):

        self.quote = quote
        self.base = base

    def __repr__(self) -> str:
        return self.normalized

    def __str__(self) -> str:
        return self.normalized

    @property
    def normalized(self) -> str:
        if self.base == self.quote:
            base = self.base
        else:
            base = f"{self.base}{self.symbol_sep}{self.quote}"
        return base


class _Symbols:
    def __init__(self):
        self.data = {}

    def clear(self):
        self.data = {}

    def set(self, exchange: str, normalized: dict):
        self.data[exchange] = {}
        self.data[exchange]['normalized'] = normalized

    def get(self, exchange: str) -> Tuple[Dict, Dict]:
        return self.data[exchange]['normalized']

    def populated(self, exchange: str) -> bool:
        return exchange in self.data

    def find(self, symbol: Union[str, Symbol]):
        ret = []

        if isinstance(symbol, Symbol):
            symbol = symbol.normalized
        for exchange, data in self.data.items():
            if symbol in data['normalized']:
                ret.append(exchange)
        return ret


Symbols = _Symbols()


def str_to_symbol(symbol: str) -> Symbol:
    '''
    symbol: str
        the symbol string must already be in correctly normalized format or this will fail
    '''
    values = symbol.split(Symbol.symbol_sep)
    return Symbol(values[0], values[1])
