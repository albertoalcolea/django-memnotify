"""Dummy backend for memnotify that does nothing (used for tests)."""


from memnotify.backends.base import BaseMemnotifyBackend


class DummyBackend(BaseMemnotifyBackend):
    def send(self, user, content, level, sender=None, expired_at=None, one_time=False):
        pass

    def num_unread(self, user):
        return 0

    def get_messages(self, user):
        return []

    def get_last_and_read(self, user):
        return None

    def mark_all_as_read(self, user):
        pass

    def global_send(self, content, level, sender=None, expired_at=None):
        pass

    def global_num_unread(self):
        return 0

    def global_get_messages(self):
        return []
