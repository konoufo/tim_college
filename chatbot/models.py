from importlib import import_module

from django.db import models
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class Conversation(models.Model):
    phone_number = models.CharField(max_length=17)
    session_id = models.CharField(max_length=9999)


def create_session_with_number(phone_number):
    s = SessionStore()
    s['phone_number'] = phone_number
    s.create()
    return s

def get_session(session_id):
    return SessionStore(session_key=session_id)

def update_session_with_context(session_id, context):
    s = get_session(session_id)
    if session_id is None:
        s.create()
    s['context'] = s.get('context', {})
    s['context'].update(context)
    s.save()
    return s

def get_current_conversation(phone_number):
    try:
        return Conversation.objects.get(phone_number=phone_number)
    except Conversation.DoesNotExist:
        return None

def create_conversation(phone_number, session_id):
    conv, _ = Conversation.objects.get_or_create(phone_number=phone_number, session_id=session_id)
    return conv
