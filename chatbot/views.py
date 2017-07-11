# -*- coding:utf8 -*-
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from chatbot.models import get_current_conversation, create_conversation, create_session_with_number, get_session
from chatbot.wit_ai_manager import client_wit

# from .queries import *
logger = logging.getLogger('chatbot.views')


class ChatDemoView(View):
    def get(self, request):
        return render(request, 'chatdemo.html')


@csrf_exempt
def inbound(request):
    message = request.POST.get('Body', None)
    user_number = request.POST.get('From', None)
    conversation = get_current_conversation(phone_number=user_number)
    try:
        logger.debug('incoming phone number: ' + user_number)
        if conversation.has_expired():
            conversation.renew_session()
        s = get_session(conversation.session_id)
    except (AttributeError, TypeError):
        s = create_session_with_number(user_number)
        create_conversation(user_number, s.session_key)
    session_id = s.session_key
    s['context'] = s.get('context', {})
    s['context'].update(client_wit.run_actions(session_id, message, s['context']))
    s.save()
    return HttpResponse('Message received: «{}»'.format(message))
