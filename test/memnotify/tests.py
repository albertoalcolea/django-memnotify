"""
Note: Select a redis db that is not in use!

    def setUp(self):
        self.notifier = RedisBackend(redis_db=?)
"""
from django.test import TestCase
from django.test.utils import override_settings

from django.contrib.auth.models import User

from memnotify.backends import base, redis_backend, dummy
from memnotify import INFO, WARNING, ERROR
import memnotify

from mock import Mock, patch

import random
import datetime


class MemnotifyConfigTestCase(TestCase):
    def test_default_backend(self):
        memnotify.reload_config()
        self.assertTrue(isinstance(memnotify._notifier, redis_backend.RedisBackend))

    @override_settings(MEMNOTIFY_BACKEND='memnotify.backends.dummy.DummyBackend')
    def test_change_backend(self):
        memnotify.reload_config()
        self.assertTrue(isinstance(memnotify._notifier, dummy.DummyBackend))


class MemnotifyShortcutsTestCase(TestCase):
    @override_settings(MEMNOTIFY_BACKEND='memnotify.backends.dummy.DummyBackend')
    def setUp(self):
        memnotify.reload_config()

    def test_send(self):
        with patch('memnotify._notifier') as mock_notifier:
            mock_notifier.send = Mock()
            user = Mock()
            memnotify.send(user, 'Message 1')
            mock_notifier.send.assert_called_with(user, 'Message 1', INFO, None, None, False)
            memnotify.send(user, 'Message 2', level=ERROR)
            mock_notifier.send.assert_called_with(user, 'Message 2', ERROR, None, None, False)
            memnotify.send(user, 'Message 3', level=WARNING, sender=user)
            mock_notifier.send.assert_called_with(user, 'Message 3', WARNING, user, None, False)
            now = datetime.datetime.now()
            memnotify.send(user, 'Message 4', level=INFO, sender=user, expired_at=now)
            mock_notifier.send.assert_called_with(user, 'Message 4', INFO, user, now, False)
            memnotify.send(user, 'Message 5', level=INFO, sender=user, expired_at=now, one_time=True)
            mock_notifier.send.assert_called_with(user, 'Message 5', INFO, user, now, True)
            memnotify.send(user, 'Message 6', level=ERROR, expired_at=now)
            mock_notifier.send.assert_called_with(user, 'Message 6', ERROR, None, now, False)

    def test_num_unread(self):
        with patch('memnotify._notifier') as mock_notifier:
            mock_notifier.num_unread = Mock(return_value=24)
            user = Mock()
            self.assertTrue(memnotify.num_unread(user), 24)
            mock_notifier.num_unread.assert_called_with(user)

    def test_get_messages(self):
        with patch('memnotify._notifier') as mock_notifier:
            messages = [Mock(), Mock(), Mock()]
            mock_notifier.get_messages = Mock(return_value=messages)
            user = Mock()
            self.assertTrue(memnotify.get_messages(user), messages)
            mock_notifier.get_messages.assert_called_with(user)

    def test_get_last_and_read(self):
        with patch('memnotify._notifier') as mock_notifier:
            msg = Mock()
            mock_notifier.get_last_and_read = Mock(return_value=msg)
            user = Mock()
            self.assertTrue(memnotify.get_last_and_read(user), msg)
            mock_notifier.get_last_and_read.assert_called_with(user)

    def test_mark_all_as_read(self):
        with patch('memnotify._notifier') as mock_notifier:
            mock_notifier.mark_all_as_read = Mock()
            user = Mock()
            self.assertTrue(memnotify.mark_all_as_read(user))
            mock_notifier.mark_all_as_read.assert_called_with(user)

    def test_global_send(self):
        with patch('memnotify._notifier') as mock_notifier:
            mock_notifier.send = Mock()
            user = Mock()
            memnotify.global_send('Message 1')
            mock_notifier.global_send.assert_called_with('Message 1', INFO, None, None)
            memnotify.global_send('Message 2', level=ERROR)
            mock_notifier.global_send.assert_called_with('Message 2', ERROR, None, None)
            memnotify.global_send('Message 3', level=WARNING, sender=user)
            mock_notifier.global_send.assert_called_with('Message 3', WARNING, user, None)
            now = datetime.datetime.now()
            memnotify.global_send('Message 4', level=INFO, sender=user, expired_at=now)
            mock_notifier.global_send.assert_called_with('Message 4', INFO, user, now)
            memnotify.global_send('Message 5', level=ERROR, expired_at=now)
            mock_notifier.global_send.assert_called_with('Message 5', ERROR, None, now)

    def test_global_num_unread(self):
        with patch('memnotify._notifier') as mock_notifier:
            mock_notifier.global_num_unread = Mock(return_value=24)
            self.assertTrue(memnotify.global_num_unread(), 24)
            mock_notifier.global_num_unread.assert_called_with()

    def test_global_get_messages(self):
        with patch('memnotify._notifier') as mock_notifier:
            messages = [Mock(), Mock(), Mock()]
            mock_notifier.global_get_messages = Mock(return_value=messages)
            self.assertTrue(memnotify.global_get_messages(), messages)
            mock_notifier.global_get_messages.assert_called_with()


class RedisBackendConfigTestCase(TestCase):
    def test_default_config(self):
        with patch('memnotify.backends.redis_backend.Redis') as mock_redis:
            notifier = redis_backend.RedisBackend()
            notifier._redis_host = 'localhost'
            notifier._redis_port = 6379
            notifier._redis_db = 0
            notifier._redis_passwd = None

    @override_settings(MEMNOTIFY_REDIS_HOST='100.100.100.100')
    @override_settings(MEMNOTIFY_REDIS_PORT=9999)
    @override_settings(MEMNOTIFY_REDIS_DB=5)
    @override_settings(MEMNOTIFY_REDIS_PASSWORD='mypass')
    def test_custom_config(self):
        with patch('memnotify.backends.redis_backend.Redis') as mock_redis:
            notifier = redis_backend.RedisBackend()
            notifier._redis_host = '100.100.100.100'
            notifier._redis_port = 9999
            notifier._redis_db = 5
            notifier._redis_passwd = 'mypass'

    @override_settings(MEMNOTIFY_REDIS_GLOBAL_KEY='mykey')
    def test_custom_global_key(self):
        with patch('memnotify.backends.redis_backend.Redis') as mock_redis:
            notifier = redis_backend.RedisBackend()
            notifier._global_key = 'mykey'


class RedisBackendTestCase(TestCase):
    def setUp(self):
        self.notifier = redis_backend.RedisBackend(redis_db=1)
        self.notifier.open()
        self.uid = random.randint(1, 999999999)
        self.user = User.objects.create(id=self.uid, username='testuser')

    def tearDown(self):
        self.notifier.redis.flushdb()

    def test_empty(self):
        self.assertEqual(self.notifier.num_unread(self.user), 0)
        self.assertEqual(self.notifier.get_messages(self.user), [])
        self.assertEqual(self.notifier.get_last_and_read(self.user), None)

    def test_send_and_get(self):
        msg_content = 'Test'
        self.notifier.send(self.user, msg_content, level=INFO)
        self.assertEqual(self.notifier.num_unread(self.user), 1)
        messages = self.notifier.get_messages(self.user)
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(self.notifier.num_unread(self.user), 1)

    def test_optional_fields(self):
        msg_content = 'Test'
        level = ERROR
        sender = self.user
        exp_date = datetime.datetime.now() + datetime.timedelta(days=1)
        self.notifier.send(self.user, msg_content, level=level, sender=self.user, expired_at=exp_date)
        self.assertEqual(self.notifier.num_unread(self.user), 1)
        messages = self.notifier.get_messages(self.user)
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(msg['level'], level)
        self.assertEqual(msg['sender'], sender)
        self.assertEqual(msg['expired_at'], exp_date)
        self.assertEqual(self.notifier.num_unread(self.user), 1)

    def test_get_last_and_read(self):
        msg_content1 = 'Test1'
        self.notifier.send(self.user, msg_content1, level=INFO)
        msg_content2 = 'Test2'
        self.notifier.send(self.user, msg_content2, level=INFO)
        self.assertEqual(self.notifier.num_unread(self.user), 2)
        msg = self.notifier.get_last_and_read(self.user)
        self.assertEqual(msg['content'], msg_content2)
        self.assertEqual(self.notifier.num_unread(self.user), 1)

    def test_mark_all_as_read(self):
        # Empty inbox
        self.assertEqual(self.notifier.num_unread(self.user), 0)
        self.notifier.mark_all_as_read(self.user)
        self.assertEqual(self.notifier.num_unread(self.user), 0)

        # Not empty inbox
        msg_content1 = 'Test1'
        msg_id1 = self.notifier.send(self.user, msg_content1, level=INFO)
        msg_content2 = 'Test2'
        msg_id2 = self.notifier.send(self.user, msg_content2, level=INFO)

        self.assertEqual(self.notifier.num_unread(self.user), 2)
        self.notifier.mark_all_as_read(self.user)
        self.assertEqual(self.notifier.num_unread(self.user), 0)

    def test_expiration_date(self):
        msg_content = 'Test'
        exp_date = datetime.datetime.now() - datetime.timedelta(days=1)
        self.notifier.send(self.user, msg_content, level=INFO, expired_at=exp_date)
        self.assertEqual(self.notifier.num_unread(self.user), 1)
        messages = self.notifier.get_messages(self.user)
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(msg['expired_at'], exp_date)
        self.assertEqual(self.notifier.num_unread(self.user), 0)
        self.assertEqual(self.notifier.get_messages(self.user), [])

    def test_one_time_msg(self):
        msg_content = 'Test'
        self.notifier.send(self.user, msg_content, level=INFO, one_time=True)
        self.assertEqual(self.notifier.num_unread(self.user), 1)
        messages = self.notifier.get_messages(self.user)
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(self.notifier.num_unread(self.user), 0)
        self.assertEqual(self.notifier.get_messages(self.user), [])

    def test_global_empty(self):
        self.assertEqual(self.notifier.global_num_unread(), 0)
        self.assertEqual(self.notifier.global_get_messages(), [])

    def test_global_send_and_get(self):
        msg_content = 'Test'
        self.notifier.global_send(msg_content, level=INFO)
        self.assertEqual(self.notifier.global_num_unread(), 1)
        messages = self.notifier.global_get_messages()
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(self.notifier.global_num_unread(), 1)

    def test_global_optional_fields(self):
        msg_content = 'Test'
        level = ERROR
        sender = self.user
        exp_date = datetime.datetime.now() + datetime.timedelta(days=1)
        self.notifier.global_send(msg_content, level=level, sender=self.user, expired_at=exp_date)
        self.assertEqual(self.notifier.global_num_unread(), 1)
        messages = self.notifier.global_get_messages()
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(msg['level'], level)
        self.assertEqual(msg['sender'], sender)
        self.assertEqual(msg['expired_at'], exp_date)
        self.assertEqual(self.notifier.global_num_unread(), 1)

    def test_global_expiration_date(self):
        msg_content = 'Test'
        exp_date = datetime.datetime.now() - datetime.timedelta(days=1)
        self.notifier.global_send(msg_content, level=INFO, expired_at=exp_date)
        self.assertEqual(self.notifier.global_num_unread(), 1)
        messages = self.notifier.global_get_messages()
        self.assertTrue(len(messages) == 1)
        msg = messages[0]
        self.assertEqual(msg['content'], msg_content)
        self.assertEqual(msg['expired_at'], exp_date)
        self.assertEqual(self.notifier.global_num_unread(), 0)
        self.assertEqual(self.notifier.global_get_messages(), [])
