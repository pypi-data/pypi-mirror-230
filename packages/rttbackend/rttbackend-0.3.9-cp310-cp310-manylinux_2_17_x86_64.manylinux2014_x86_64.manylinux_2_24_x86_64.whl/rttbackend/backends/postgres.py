
import asyncpg
from typing import Tuple
from rttbackend.defines import *
from datetime import datetime as dt
from rttbackend.config import Config
import json


class CredsPostgres():
    def __init__(self):
        pass


class TargetPostgres(CredsPostgres):
    id = POSTGRES

    def __init__(self, config=None):
        if config is None:
            config = 'config.yaml'

        self.config = Config(config=config)
        keys = self.config[self.id.lower()]
        self.host = keys.host
        self.user = keys.user
        self.pw = keys.pw
        self.db = keys.db
        self.port = keys.port


class Postgres():
    def __init__(self, conn: CredsPostgres):
        self.table = self.default_table
        self.raw_table = TABLE + RAW

        self.host = conn.host
        self.user = conn.user
        self.pw = conn.pw
        self.db = conn.db
        self.port = conn.port

    def _raw(self, data: Tuple):
        timestamp, data = data
        return f"('{timestamp}','{json.dumps(data)}')"

    async def _connect(self):
        self.conn = await asyncpg.connect(user=self.user, password=self.pw, database=self.db, host=self.host, port=self.port)

    async def read(self):
        await self._connect()
        args_str = self._read()
        async with self.conn.transaction():
            try:
                return await self.conn.fetch(f"SELECT {args_str} FROM {self.table}")
            except Exception as a:
                print(a)
                # when restarting a subscription, some exchanges will re-publish a few messages
                pass

    async def write(self, updates: list):
        await self._connect()

        batch = []

        for data in updates:
            data = data.to_dict(numeric_type=float)
            ts = dt.utcfromtimestamp(
                data['timestamp']) if data['timestamp'] else None
            batch.append((ts, data))

        args_str = ([self._write(u) for u in batch])
        args_raw_str = ','.join([self._raw(u) for u in batch])
        self.n = ', '.join([f'${i+1}' for i in range(len(args_str[0]))])
        self.col = self._col()

        async with self.conn.transaction():
            try:
                await self.conn.executemany(f'INSERT INTO {self.table}{self.col} VALUES({self.n}) ON CONFLICT DO NOTHING', args_str)
                await self.conn.execute(f"INSERT INTO {self.raw_table} VALUES {args_raw_str}")
            except Exception as a:
                print(a)
                # when restarting a subscription, some exchanges will re-publish a few messages
                pass

    async def delete(self, updates: list):
        await self._connect()
        batch = []

        for data in updates:
            data = data.to_dict(numeric_type=float)
            ts = dt.utcfromtimestamp(
                data['timestamp']) if data['timestamp'] else None
            batch.append((ts, data))

        args_str = ([self._delete(u) for u in batch])
        args_raw_str = ','.join([self._raw(u) for u in batch])
        self.n = self._delete_col()
        async with self.conn.transaction():
            try:
                await self.conn.executemany(f'DELETE FROM {self.table} WHERE {self.n}', args_str)

            except Exception as a:
                print(a)
                # when restarting a subscription, some exchanges will re-publish a few messages
                pass


class RefreshSymbolPostgres(Postgres):
    default_table = TABLE + REFRESH_SYMBOL

    def _read(self):
        return f"timestamp,exchange,symbol,base_symbol,quote_symbol"

    def _col(self):
        return f"(exchange,symbol,base_symbol,quote_symbol,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['exchange'], data['symbol'], data['base_symbol'], data['quote_symbol'], timestamp)


class ExchangePostgres(Postgres):
    default_table = TABLE + EXCHANGE

    def _read(self):
        return f"id,exchange"

    def _col(self):
        return f"(exchange,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['exchange'], timestamp)


class BaseSymbolPostgres(Postgres):
    default_table = TABLE + BASE_SYMBOL

    def _read(self):
        return f"id,base_symbol"

    def _col(self):
        return f"(base_symbol,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['base_symbol'], timestamp)


class QuoteSymbolPostgres(Postgres):
    default_table = TABLE + QUOTE_SYMBOL

    def _read(self):
        return f"id,quote_symbol"

    def _col(self):
        return f"(quote_symbol,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['quote_symbol'], timestamp)


class SymbolPostgres(Postgres):
    default_table = TABLE + SYMBOL

    def _read(self):
        return f"id,symbol,base_symbol_id,quote_symbol_id,exchange_id,timestamp"

    def _col(self):
        return f"(exchange_id,base_symbol_id,quote_symbol_id,symbol,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['exchange_id'], data['base_symbol_id'], data['quote_symbol_id'], data['symbol'], timestamp)


class RefreshSymbolLookupPostgres(Postgres):
    default_table = TABLE + REFRESH_SYMBOL_LOOKUP

    def _read(self):
        return f"timestamp,exchange,base_symbol,quote_symbol,name,type,description,symbol_exchange,region,market_open,market_close,time_zone,cik,country,sector,industry,address,figi,mic,ipo,phone,website,logo"

    def _col(self):
        return f"(timestamp,exchange,base_symbol,quote_symbol,name,type,description,symbol_exchange,region,market_open,market_close,time_zone,cik,country,sector,industry,address,figi,mic,ipo,phone,website,logo)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['exchange'], data['base_symbol'], data['quote_symbol'], data['name'], data['type'], data['description'], data['symbol_exchange'], data['region'], data['market_open'], data['market_close'], data['time_zone'], data['cik'], data['country'], data['sector'], data['industry'], data['address'], data['figi'], data['mic'], data['ipo'], data['phone'], data['website'], data['logo'])


class NamePostgres(Postgres):
    default_table = TABLE + NAME

    def _read(self):
        return f"id,name"

    def _col(self):
        return f"(name,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['name'], data['exchange_id'], timestamp)


class TypePostgres(Postgres):
    default_table = TABLE + TYPE

    def _read(self):
        return f"id,type"

    def _col(self):
        return f"(type,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['type'], data['exchange_id'], timestamp)


class DescriptionPostgres(Postgres):
    default_table = TABLE + DESCRIPTION

    def _read(self):
        return f"id,description"

    def _col(self):
        return f"(description,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['description'], data['exchange_id'], timestamp)


class SymbolExchangePostgres(Postgres):
    default_table = TABLE + SYMBOL_EXCHANGE

    def _read(self):
        return f"id,symbol_exchange"

    def _col(self):
        return f"(symbol_exchange,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['symbol_exchange'], data['exchange_id'], timestamp)


class CIKPostgres(Postgres):
    default_table = TABLE + CIK

    def _read(self):
        return f"id,cik"

    def _col(self):
        return f"(cik,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['cik'], data['exchange_id'], timestamp)


class CountryPostgres(Postgres):
    default_table = TABLE + COUNTRY

    def _read(self):
        return f"id,country"

    def _col(self):
        return f"(country,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['country'], data['exchange_id'], timestamp)


class SectorPostgres(Postgres):
    default_table = TABLE + SECTOR

    def _read(self):
        return f"id,sector"

    def _col(self):
        return f"(sector,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['sector'], data['exchange_id'], timestamp)


class IndustryPostgres(Postgres):
    default_table = TABLE + INDUSTRY

    def _read(self):
        return f"id,industry"

    def _col(self):
        return f"(industry,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['industry'], data['exchange_id'], timestamp)


class AddressPostgres(Postgres):
    default_table = TABLE + ADDRESS

    def _read(self):
        return f"id,address"

    def _col(self):
        return f"(address,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['address'], data['exchange_id'], timestamp)


class IPOPostgres(Postgres):
    default_table = TABLE + IPO

    def _read(self):
        return f"id,ipo"

    def _col(self):
        return f"(ipo,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['ipo'], data['exchange_id'], timestamp)


class PhonePostgres(Postgres):
    default_table = TABLE + PHONE

    def _read(self):
        return f"id,phone"

    def _col(self):
        return f"(phone,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['phone'], data['exchange_id'], timestamp)


class WebsitePostgres(Postgres):
    default_table = TABLE + WEBSITE

    def _read(self):
        return f"id,website"

    def _col(self):
        return f"(website,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['website'], data['exchange_id'], timestamp)


class LogoPostgres(Postgres):
    default_table = TABLE + LOGO

    def _read(self):
        return f"id,logo"

    def _col(self):
        return f"(logo,exchange_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['logo'], data['exchange_id'], timestamp)


class SymbolLookupPostgres(Postgres):
    default_table = TABLE + SYMBOL_LOOKUP

    def _read(self):
        return NotImplemented

    def _col(self):
        return f"(exchange_id,base_symbol_id,quote_symbol_id,name_id,type_id,description_id,symbol_exchange_id,cik_id,country_id,sector_id,industry_id,address_id,ipo_id,phone_id,website_id,logo_id,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['exchange_id'], data['base_symbol_id'], data['quote_symbol_id'], data['name_id'], data['type_id'], data['description_id'], data['symbol_exchange_id'], data['cik_id'], data['country_id'], data['sector_id'], data['industry_id'], data['address_id'], data['ipo_id'], data['phone_id'], data['website_id'],  data['logo_id'], timestamp)


class RefreshSymbolPeersPostgres(Postgres):
    default_table = TABLE + REFRESH_SYMBOL_PEERS

    def _read(self):
        return f"exchange,base_symbol,peer_symbol"

    def _col(self):
        return f"(timestamp,exchange,base_symbol,peer_symbol)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['exchange'], data['base_symbol'], data['peer_symbol'])


class SymbolPeersPostgres(Postgres):
    default_table = TABLE + SYMBOL_PEERS

    def _read(self):
        return f"exchange_id,base_symbol_id,peer_symbol_id"

    def _col(self):
        return f"(timestamp,exchange_id,base_symbol_id,peer_symbol_id)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['exchange_id'], data['base_symbol_id'], data['peer_symbol_id'])


class RefreshSymbolGainersLosersPostgres(Postgres):
    default_table = TABLE + REFRESH_SYMBOL_GAINERS_LOSERS

    def _read(self):
        return f"exchange,base_symbol,quote_symbol,movement,price,change_amount,change_percentage,volume,name"

    def _col(self):
        return f"(timestamp,exchange,base_symbol,quote_symbol,movement,price,change_amount,change_percentage,volume,name)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['exchange'], data['base_symbol'], data['quote_symbol'], data['movement'], data['price'], data['change_amount'], data['change_percentage'], data['volume'], data['name'])


class MovementPostgres(Postgres):
    default_table = TABLE + MOVEMENT

    def _read(self):
        return f"id,movement"

    def _col(self):
        return f"(timestamp,movement)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['movement'])


class SymbolGainersLosersPostgres(Postgres):
    default_table = TABLE + SYMBOL_GAINERS_LOSERS

    def _read(self):
        return f"id,movement"

    def _col(self):
        return f"(timestamp,exchange_id,base_symbol_id,quote_symbol_id,movement_id,price,change_amount,change_percentage,volume)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (timestamp, data['exchange_id'], data['base_symbol_id'], data['quote_symbol_id'], data['movement_id'], data['price'], data['change_amount'], data['change_percentage'], data['volume'])


class SubscriptionPostgres(Postgres):
    default_table = VIEW + SUBSCRIPTION

    def _read(self):
        return f"symbol_id,exchange_id"


class SyncSubscriptionPostgres(Postgres):
    default_table = TABLE + SYNC_SUBSCRIPTION

    def _read(self):
        return f"symbol,exchange"

    def _col(self):
        return f"(symbol,exchange,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['symbol'], data['exchange'], timestamp)

    def _delete_col(self):
        return f"symbol = ($1) AND exchange = ($2)"

    def _delete(self, data: Tuple):
        timestamp, data = data
        symbol = data['symbol']
        exchange = data['exchange']

        return (data['symbol'],  data['exchange'])


class SymbolOverviewSubscriptionPostgres(Postgres):
    default_table = VIEW + SYMBOL_OVERVIEW_SUBSCRIPTION

    def _read(self):
        return f"base_symbol_id,quote_symbol_id,name_id,type_id,description_id,symbol_exchange_id,cik_id,country_id"

class SyncSymbolOverviewSubscriptionPostgres(Postgres):
    default_table = TABLE + SYNC_SYMBOL_OVERVIEW_SUBSCRIPTION

    def _read(self):
        return f"base_symbol,quote_symbol,name,type,description,symbol_exchange,cik,country"

    def _col(self):
        return f"(base_symbol,quote_symbol,name,type,description,symbol_exchange,cik,country,timestamp)"

    def _write(self, data: Tuple):
        timestamp, data = data
        return (data['base_symbol'], data['quote_symbol'], data['name'], data['type'], data['description'], data['symbol_exchange'], data['cik'], data['country'], timestamp)

    def _delete_col(self):
        return f"base_symbol = ($1) AND quote_symbol = ($2)"

    def _delete(self, data: Tuple):
        timestamp, data = data
        base_symbol = data['base_symbol']
        quote_symbol = data['quote_symbol']

        return (data['base_symbol'],  data['quote_symbol'])
