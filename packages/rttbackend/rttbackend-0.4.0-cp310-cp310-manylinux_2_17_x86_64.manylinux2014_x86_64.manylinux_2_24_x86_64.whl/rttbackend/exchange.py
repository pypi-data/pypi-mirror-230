'''
Copyright (C) 2017-2023 Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
import asyncio
from decimal import Decimal
import logging

import time
from datetime import datetime as dt, timezone
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Union


from rttbackend.defines import REFRESH_SYMBOL, REFRESH_SYMBOL_LOOKUP
from rttbackend.symbols import Symbol, Symbols
from rttbackend.connection import HTTPSync, RestEndpoint
from rttbackend.exceptions import UnsupportedDataFeed, UnsupportedSymbol, UnsupportedTradingOption
from rttbackend.config import Config
from rttbackend.backends.redis import ExchangeRedis, TargetRedis

from prefect import flow, task
LOG = logging.getLogger('feedhandler')

conn_redis = ExchangeRedis(TargetRedis())


class Exchange:
    id = NotImplemented
    websocket_endpoints = NotImplemented
    rest_endpoints = NotImplemented
    _parse_symbol_data = NotImplemented
    websocket_channels = NotImplemented
    rest_channels = NotImplemented
    request_limit = NotImplemented
    valid_candle_intervals = NotImplemented
    candle_interval_map = NotImplemented
    http_sync = HTTPSync()

    allow_empty_subscriptions = False
    initialized_timestamp = time.time()

    def __init__(self, config=None, sandbox=False, subaccount=None, symbols=None, **kwargs):
        self.config = Config(config=config)
        self.sandbox = sandbox
        self.subaccount = subaccount

        keys = self.config[self.id.lower(
        )] if self.subaccount is None else self.config[self.id.lower()][self.subaccount]
        self.key_id = keys.key_id
        self.key_secret = keys.key_secret
        self.key_passphrase = keys.key_passphrase
        self.account_name = keys.account_name

        self.ignore_invalid_instruments = self.config.ignore_invalid_instruments

        if not Symbols.populated(self.id):
            self.symbol_mapping(key_id=self.key_id)

        self.normalized_symbol_mapping = Symbols.get(self.id)
        self.exchange_symbol_mapping = {
            value: key for key, value in self.normalized_symbol_mapping.items()}
        self.subscription = [None]

        if symbols:
            data = []
            for symbol in symbols:
                try:
                    data.append(self.std_symbol_to_exchange_symbol(symbol))
                    self.subscription = symbols
                except UnsupportedSymbol:
                    pass
            self.subscription = data

    @classmethod
    def timestamp_normalize(cls, ts: dt) -> float:
        return ts.astimezone(timezone.utc).timestamp()

    @classmethod
    def normalize_order_options(cls, option: str):
        if option not in cls.order_options:
            raise UnsupportedTradingOption
        return cls.order_options[option]

    @classmethod
    def info(cls) -> Dict:
        """
        Return information about the Exchange for REST and Websocket data channels
        """
        symbols = cls.symbol_mapping()
        data = Symbols.get(cls.id)[1]
        data['symbols'] = list(symbols.keys())
        data['channels'] = {
            'rest': list(cls.rest_channels) if hasattr(cls, 'rest_channels') else [],
            'websocket': list(cls.websocket_channels.keys())
        }
        return data

    @classmethod
    def manager(cls) -> Dict:
        """
        Return current state of the exchange.
        """
        data = {}
        data['initialized_timestamp'] = cls.initialized_timestamp
        data['id'] = cls.id
        return data

    @classmethod
    def symbols(cls, refresh=False) -> list:
        return list(cls.symbol_mapping(refresh=refresh).keys())

    @classmethod
    def _symbol_endpoint_prepare(cls, ep: RestEndpoint, key_id=None) -> Union[List[str], str]:
        """
        override if a specific exchange needs to do something first, like query an API
        to get a list of currencies, that are then used to build the list of symbol endpoints
        """
        return ep.route('instruments')

    @classmethod
    def _get_symbol_data(cls, key_id=None):
        data = []

        for ep in cls.rest_endpoints:
            addr = cls._symbol_endpoint_prepare(ep, key_id=key_id)
            if isinstance(addr, list):
                for ep in addr:
                    LOG.debug(
                        "%s: reading symbol information from %s", cls.id, ep)
                    data.append(cls.http_sync.read(
                        ep, json=True, uuid=cls.id, isCache=False))
            else:
                LOG.debug("%s: reading symbol information from %s", cls.id, addr)
                data.append(cls.http_sync.read(
                    addr, json=True, uuid=cls.id, isCache=False))

        return data

    @classmethod
    def symbol_mapping(cls, key_id=None, refresh=False) -> Dict:

        if Symbols.populated(cls.id) and not refresh:
            return Symbols.get(cls.id)
        try:
            res = conn_redis.read(cls.id)

            if res is not None:
                Symbols.set(cls.id, res)
                return res

            data = cls._get_symbol_data(key_id)

            syms = cls._parse_symbol_data(
                data if len(data) > 1 else data[0])

            conn_redis.write(cls.id, syms)

            Symbols.set(cls.id, syms)

            return syms
        except Exception as e:
            LOG.error("%s: Failed to parse symbol information: %s",
                      cls.id, str(e), exc_info=True)
            raise

    @classmethod
    def std_channel_to_exchange(cls, channel: str) -> str:
        try:
            if cls.rest_channels is not NotImplemented:
                return {**cls.websocket_channels, **cls.rest_channels}[channel]
            return cls.websocket_channels[channel]

        except KeyError:
            raise UnsupportedDataFeed(
                f'{channel} is not supported on {cls.id}')

    @classmethod
    def exchange_channel_to_std(cls, channel: str) -> str:

        if cls.rest_channels is not NotImplemented:
            total_channels = {**cls.websocket_channels, **cls.s}
        else:
            total_channels = {**cls.websocket_channels}

        for chan, exch in total_channels.items():
            if exch == channel:
                return chan
        raise ValueError(f'Unable to normalize channel {cls.id}')

    def exchange_symbol_to_std_symbol(self, symbol: str) -> str:
        try:
            return self.exchange_symbol_mapping[symbol]
        except KeyError:
            if self.ignore_invalid_instruments:
                LOG.warning('Invalid symbol %s configured for %s',
                            symbol, self.id)
                return symbol
            raise UnsupportedSymbol(f'{symbol} is not supported on {self.id}')

    def std_symbol_to_exchange_symbol(self, symbol: Union[str, Symbol]) -> str:
        if isinstance(symbol, Symbol):
            symbol = symbol.normalized
        try:
            return self.normalized_symbol_mapping[symbol]
        except KeyError:
            if self.ignore_invalid_instruments:
                LOG.warning('Invalid symbol %s configured for %s',
                            symbol, self.id)
                return symbol
            raise UnsupportedSymbol(f'{symbol} is not supported on {self.id}')

    async def refresh_symbol(self):
        raise NotImplementedError


class RestExchange:
    def refresh_symbol_lookup(self):
        raise NotImplementedError
