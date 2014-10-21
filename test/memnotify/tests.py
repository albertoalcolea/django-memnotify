"""
Note: Select a redis db that is not in use!

    def setUp(self):
        self.notifier = RedisBackend(redis_db=?)
"""
from django.test import TestCase
from django.contrib.auth.models import User
from memnotify.backends.redis_backend import RedisBackend
from memnotify import INFO, ERROR

import random
import datetime


class RedisBackendTestCase(TestCase):
    def setUp(self):
        self.notifier = RedisBackend(redis_db=1)
        self.notifier.open()
        self.uid = random.randint(1, 999999999)
        while self.notifier.redis.exists(self.uid):
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
