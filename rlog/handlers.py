# coding: utf-8
import logging
import redis

from .formatters import JSONFormatter, DictFormatter


class RedisHandler(logging.Handler):
    """
    Publish messages to redis channel.
    """

    def __init__(self, channel, redis_client=None,
                 formatter=DictFormatter(),
                 level=logging.NOTSET, **redis_kwargs):
        """
        Create a new logger for the given channel and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.channel = channel
        self.redis_client = redis_client or redis.Redis(**redis_kwargs)
        self.formatter = formatter

    def emit(self, record):
        """
        Publish record to redis logging channel
        """
        try:
            self.redis_client.publish(self.channel, self.format(record))
        except redis.RedisError:
            pass


class RedisListHandler(logging.Handler):

    def __init__(self, key, max_messages=None, redis_client=None,
                 formatter=JSONFormatter(), ttl=None,
                 level=logging.NOTSET, **redis_kwargs):
        """
        Create a new logger for the given key and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.key = key
        self.redis_client = redis_client or redis.Redis(**redis_kwargs)
        self.formatter = formatter
        self.max_messages = max_messages
        self.ttl = ttl

    def emit(self, record):
        """
        Publish record to redis logging list
        """
        try:
            if self.max_messages:
                p = self.redis_client.pipeline()
                p.rpush(self.key, self.format(record))
                p.ltrim(self.key, -self.max_messages, -1)
                p.execute()
            else:
                self.redis_client.rpush(self.key, self.format(record))
            if self.ttl:
                self.redis_client.expire(self.key, self.ttl)
        except redis.RedisError:
            pass

class RedisStreamHandler(logging.Handler):

    def __init__(self, key, max_messages=None, redis_client=None,
                 formatter=JSONFormatter(), ttl=None,
                 level=logging.NOTSET, **redis_kwargs):
        """
        Create a new logger for the given key and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.key = key
        self.redis_client = redis_client or redis.Redis(**redis_kwargs)
        self.formatter = formatter
        self.max_messages = max_messages
        self.ttl = ttl

    def emit(self, record):
        """
        Publish record to redis logging list
        """
        try:
            if self.max_messages:
                self.redis_client.xadd(self.key, maxlen=self.max_messages, **self.format(record))
            else:
                self.redis_client.xadd(self.key, **self.format(record))
            if self.ttl:
                self.redis_client.expire(self.key, self.ttl)
        except redis.RedisError:
            pass
