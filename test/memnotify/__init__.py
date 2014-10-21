"""
Tools for sending in-memory notifications.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string


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
_DEFAULT_BACKEND = 'memnotify.backends.redis_backend.RedisBackend'
_backend_str = getattr(settings, 'MEMNOTIFY_BACKEND', _DEFAULT_BACKEND)
_backend = import_string(_backend_str or _DEFAULT_BACKEND)
_notifier = _backend()

def reload_config(backend=None):
    global _backend_str
    global _backend
    global _notifier
    if backend is not None:
        _backend = import_string(backend)
        _notifier = _backend()
    else:
        _backend_str = getattr(settings, 'MEMNOTIFY_BACKEND', _DEFAULT_BACKEND)
        _backend = import_string(_backend_str or _DEFAULT_BACKEND)
        _notifier = _backend()


"""
Shortcut for memnotify methods
"""
def send(user, content, level=INFO, sender=None, expired_at=None, one_time=False):
    with _notifier as connection:
        return _notifier.send(user, content, level, sender, expired_at, one_time)

def num_unread(user):
    with _notifier as connection:
        return _notifier.num_unread(user)

def get_messages(user):
    with _notifier as connection:
        return _notifier.get_messages(user)

def get_last_and_read(user):
    with _notifier as connection:
        return _notifier.get_last_and_read(user)

def mark_all_as_read(user):
    with _notifier as connection:
        return _notifier.mark_all_as_read(user)

def global_send(content, level=INFO, sender=None, expired_at=None):
    with _notifier as connection:
        return _notifier.global_send(content, level, sender, expired_at)

def global_num_unread():
    with _notifier as connection:
        return _notifier.global_num_unread()

def global_get_messages():
    with _notifier as connection:
        return _notifier.global_get_messages()
