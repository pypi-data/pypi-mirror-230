
from rttbackend.defines import *
from prefect import task, flow, get_run_logger
from rttbackend.backends.postgres import *
from rttbackend.exchanges import AlphaVantage
from rttbackend.exchanges import Finnhub
from rttbackend.exchanges import Fmp




def is_exchange_valid(exchanges):
    if [exchange for exchange in exchanges if exchange not in EXCHANGES_LIST]:
        return


def get_all_exhanges(exchanges):
    if exchanges == [ALL_EXCHANGES]:
        return EXCHANGES_LIST
    return exchanges


def has_method(o, name):
    return callable(getattr(o, name, None))


@task
def _initiate(exchange, symbols):
    if exchange == ALPHAVANTAGE:
        return AlphaVantage(config='config.yaml', symbols=symbols)
    elif exchange == FINNHUB:
        return Finnhub(config='config.yaml', symbols=symbols)
    elif exchange == FMP:
        return Fmp(config='config.yaml', symbols=symbols)


@task
def _initiate_connection(feed, type):

    try:
        if feed is None:
            return None
        if feed[type] is None:
            return None
        return feed[type](), feed
    except AttributeError:
        return None


@task(retries=2, retry_delay_seconds=5)
def _extract(feed, method, symbol):
    if symbol is None:
        return feed[method](), method, feed, None
    return feed[method](symbol), method, feed, symbol


@task
async def _extract_database(conn):
    return await conn[0].read(), conn[1]


@task
def _transform(symbol, feed, method, data, table):
    return feed.message_handler(method, data, symbol), table


@task
async def _load(conn, data):

    await conn[0].write(data)


@task
async def _delete(conn, data):
    await conn[0].delete(data)


def init_paramteter(data):
    # need to convert to array
    if type(data) == str:
        return [data]
    return data


def get_feeds(exchanges, symbols):
    return [_initiate.submit(exchange, symbols) for exchange in exchanges]


def get_conn(feeds, type):
    return [_initiate_connection.submit(feed.result(), type) for feed in feeds]


def get_extract(conns):
    return [_extract.submit(conn.result()[1], method, sub)
            for conn in conns if conn.result() is not None for sub in conn.result()[1].subscription for method in conn.result()[0]]


def get_transform(extract, table):
    return [_transform.submit(e.result()[3], e.result()[2], e.result()[1], e.result()[0], table) for e in extract]


def prepare_load(transform, db_conns):
    return [(conn, [res for raw in transform if raw.result() is not None if raw.result()[0] is not None if raw.result()[1] == conn[1] for res in raw.result()[0]])
            for conn in db_conns.result()]


async def get_load(conns):

    return [await _load.submit(conn[0], conn[1]) for conn in conns if conn[1] != []]


async def get_delete(conns, wait=None):
    return [await _delete.submit(conn[0], conn[1], wait_for=wait) for conn in conns if conn[1] != []]


async def get_extract_database(conns, wait=None):
    return [await _extract_database.submit(conn, wait_for=wait) for conn in conns]
