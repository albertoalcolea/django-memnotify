"""
Tools for sending in-memory notifications.
"""
from __future__ import unicode_literals

from django.conf import settings


__VERSION__ = 0.1


"""
Message levels
"""
DEBUG = 10
INFO = 20
ERROR = 30
WARNING = 40
CRITICAL = 50


"""
memnotify backend configuration
"""
_notifier = None


"""
Shortcut for memnotify methods
"""
def send(user, content, level=INFO, sender=None, expired_at=None, one_time=False):
    return _notifier.send(user, content, level, sender, expired_at, one_time)

def num_unread(user):
    return _notifier.num_unread(user)

def get_messages(user):
    return _notifier.get_messages(user)

def get_last_and_read(user):
    return _notifier.get_last_and_read(user)

def mark_all_as_read(user):
    return _notifier.mark_all_as_read(user)

def global_send(content, level=INFO, sender=None, expired_at=None):
    return _notifier.global_send(content, level, sender, expired_at)

def global_num_unread():
    return _notifier.global_num_unread()

def global_get_messages():
    return _notifier.global_get_messages()
