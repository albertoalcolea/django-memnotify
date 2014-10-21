# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from memnotify.notifier import Notifier

notifier = Notifier()


def index(request):
	messages = notifier.get_messages(request.user)
	return HttpResponse('This is a test\n\n{0}'.format(messages))