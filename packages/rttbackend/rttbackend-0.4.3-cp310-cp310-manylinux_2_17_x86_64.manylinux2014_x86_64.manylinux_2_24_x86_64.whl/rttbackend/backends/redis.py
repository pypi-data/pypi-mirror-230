
import redis
from typing import Tuple
from rttbackend.defines import POSTGRES, REDIS, CONNECTION, REFRESH_SYMBOL, TABLE, EXCHANGE, BASE_SYMBOL, QUOTE_SYMBOL, SYMBOL, RAW, API, REFRESH_SYMBOL_LOOKUP
from datetime import datetime as dt
from rttbackend.config import Config
from yapic import json as json_parser


class CredsRedis():
    def __init__(self):
        pass


class TargetRedis(CredsRedis):
    id = REDIS

    def __init__(self, config=None):
        if config is None:
            config = 'config.yaml'

        self.config = Config(config=config)
        keys = self.config[self.id.lower()]
        self.host = keys.host
        self.port = keys.port


class Redis():
    def __init__(self, conn: CredsRedis):
        self.key = self.default_key
        self.expire_in_s = self.default_expire_in_s
        self.raw_table = TABLE + RAW

        self.host = conn.host
        self.port = conn.port

    def _connect(self):
        self.conn = redis.Redis(
            host=self.host, port=self.port, decode_responses=True)

    def read(self, name):
        self._connect()
        try:
            return json_parser.loads(self.conn.get(f"{self.key}:{name}"))
        except:
            return None

    def write(self, name, data):
        self._connect()
        self.conn.set(f"{self.key}:{name}",
                      json_parser.dumps(data, default=str),  ex=self.expire_in_s)

        self.conn.xadd(f"{self.key}", 
                       {"Key: ": json_parser.dumps(name, default=str),
                        "Value: ": json_parser.dumps(data, default=str)
                        })
 
    def subscribe(self):
        self._connect()
        return self.conn.xread({f"{self.key}":'$'}, block = 1000)
    
    def subscribe_key(self): 
        self._connect()

        pubsub = self.conn.pubsub()
        pubsub.psubscribe("__keyspace@0__:*")
        return pubsub
        
    def get_previous_message(self):
        self._connect()
        return self.conn.xrange(f"{self.key}")

class ConnectionRedis(Redis):
    default_key = CONNECTION
    default_expire_in_s = 300  # 5 minute


class ExchangeRedis(Redis):
    default_key = EXCHANGE
    default_expire_in_s = None  # never expired

class APIRedis(Redis):
    default_key  = API
    default_expire_in_s = None  # never expired