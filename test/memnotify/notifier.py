from redis import Redis

import datetime
import cPickle





class Notifier(object):
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0, password=None)
        self.global_key = 'GLOBAL_MSG'

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

    def send(self, user, content, level=INFO, sender=None, expired_at=None, one_time=False):
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

    def global_send(self, content, level=INFO, sender=None, expired_at=None):
        msg = self._generate_msg(content, level, sender, expired_at)
        self.redis.rpush(self.global_key, self._codify(msg))

    def global_num_unread(self):
        return self.redis.llen(self.global_key)

    def global_get_messages(self):
        messages = []
        for raw_msg in self.redis.lrange(self.global_key, 0, -1):
            msg = self._decodify(raw_msg)
            self._check_expiration(self.global_key, msg, raw_msg)
            messages.append(msg)
        return messages
