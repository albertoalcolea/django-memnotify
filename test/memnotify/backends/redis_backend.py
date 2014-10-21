"""Backend for memnotify that uses Redis."""

from redis import Redis

import datetime
import cPickle

from django.conf import settings

from memnotify.backends.base import BaseMemnotifyBackend


class RedisBackend(BaseMemnotifyBackend):
    def __init__(self, *args, **kwargs):
        self.redis = None
        if 'redis_host' in kwargs:
            self._redis_host = kwargs.pop('redis_host')
        else:
            self._redis_host = getattr(settings, 'MEMNOTIFY_REDIS_HOST', 'localhost')
        if 'redis_port' in kwargs:
            self._redis_port = kwargs.pop('redis_port')
        else:
            self._redis_port = getattr(settings, 'MEMNOTIFY_REDIS_PORT', 6379)
        if 'redis_db' in kwargs:
            self._redis_db = kwargs.pop('redis_db')
        else:
            self._redis_db = getattr(settings, 'MEMNOTIFY_REDIS_DB', 6379)
        if 'redis_passwd' in kwargs:
            self._redis_passwd = kwargs.pop('redis_passwd')
        else:
            self._redis_passwd = getattr(settings, 'MEMNOTIFY_REDIS_PASSWORD', None)
        if 'global_key' in kwargs:
            self._global_key = kwargs.pop('global_key')
        else:
            self._global_key = getattr(settings, 'MEMNOTIFY_REDIS_GLOBAL_KEY', 'GLOBAL_MSG')
        super(RedisBackend, self).__init__(*args, **kwargs)

    def _get_key(self, user):
        return user.id

    def _codify(self, decod_msg):
        return cPickle.dumps(decod_msg)

    def _decodify(self, cod_msg):
        return cPickle.loads(cod_msg)

    def _generate_msg(self, content, level, sender, expired_at, one_time=False):
        msg = {
            'content': content,
            'level': level,
            'created_at': datetime.datetime.now(),
            'sender': sender,
            'expired_at': expired_at,
        }
        if one_time:
            msg['one_time'] = True
        return msg

    def _check_expiration(self, key, msg, raw_msg):
        expired = False
        exp_date = msg['expired_at']
        if exp_date is not None and exp_date <= datetime.datetime.now():
            expired = True
        if 'one_time' in msg:
            expired = True
        if expired:
            self.redis.lrem(key, raw_msg)
        return expired

    def open(self):
        if self.redis is None:
            self.redis = Redis(
                host=self._redis_host,
                port=self._redis_port,
                db=self._redis_db,
                password=self._redis_passwd
            )
            return True
        return False

    def close(self):
        if self.redis is not None:
            # Does Redis a "close" or "disconnect" method?
            del(self.redis)

    def send(self, user, content, level, sender=None, expired_at=None, one_time=False):
        key = self._get_key(user)
        msg = self._generate_msg(content, level, sender, expired_at, one_time=one_time)
        self.redis.rpush(key, self._codify(msg))

    def num_unread(self, user):
        key = self._get_key(user)
        return self.redis.llen(key)

    def get_messages(self, user):
        key = self._get_key(user)
        messages = []
        for raw_msg in self.redis.lrange(key, 0, -1):
            msg = self._decodify(raw_msg)
            self._check_expiration(key, msg, raw_msg)
            messages.append(msg)
        return messages

    def get_last_and_read(self, user):
        key = self._get_key(user)
        raw_msg = self.redis.rpop(key)
        if raw_msg is not None:
            return self._decodify(raw_msg)
        else:
            return None

    def mark_all_as_read(self, user):
        key = self._get_key(user)
        self.redis.delete(key)

    def global_send(self, content, level, sender=None, expired_at=None):
        msg = self._generate_msg(content, level, sender, expired_at)
        self.redis.rpush(self._global_key, self._codify(msg))

    def global_num_unread(self):
        return self.redis.llen(self._global_key)

    def global_get_messages(self):
        messages = []
        for raw_msg in self.redis.lrange(self._global_key, 0, -1):
            msg = self._decodify(raw_msg)
            self._check_expiration(self._global_key, msg, raw_msg)
            messages.append(msg)
        return messages
