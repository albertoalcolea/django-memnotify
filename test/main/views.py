# -*- coding: utf-8 -*-
from django.shortcuts import render
import memnotify


def index(request):
	notifications = []
	if request.user.is_authenticated():
		notifications = memnotify.get_messages(request.user)
	return render(request, 'index.html', {'notifications': notifications})
