from importlib import import_module
import uuid, logging

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sessions.models import Session
from django.utils import timezone


try:
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
except ImproperlyConfigured:
    SessionStore = import_module('django.contrib.sessions.backends.db').SessionStore


logger = logging.getLogger('chatbot.models')


class Conversation(models.Model):
    phone_number = models.CharField(max_length=17)
    session_id = models.CharField(max_length=9999)

    def renew_session(self):
        s = create_session_with_number(self.phone_number)
        self.session_id = s.session_key
        self.save()

    def has_expired(self):
        if SessionStore().exists(session_key=self.session_id):
            return SessionStore(session_key=self.session_id).get_expiry_date() <= timezone.now()
        return True


def create_session_with_number(phone_number):
    s = SessionStore()
    s['phone_number'] = phone_number
    s.create()
    return s


def create_session(session_id=None):
    if isinstance(session_id, uuid.UUID):
        s = Session(expire_date=timezone.now() + timezone.timedelta(hours=1))
        s.pk = str(session_id)
        s.save()
        return s
    s = SessionStore()
    s.create()
    return s


def get_session(session_id):
    if isinstance(session_id, uuid.UUID):
        session_id = str(session_id)
    if not SessionStore().exists(session_key=session_id):
        raise Exception('No session with this id.')
    return SessionStore(session_key=session_id)


def update_session_with_context(session_id, context):
    s = get_session(session_id)
    s['context'] = s.get('context', {})
    s['context'].update(context)
    s.save()
    return s


def create_session_with_context(context):
    s = SessionStore()
    s.create()
    s['context'].update(context)
    return s


def update_or_create_with_context(session_id, context):
    try:
        s = update_session_with_context(session_id, context)
    except Exception as e:
        logger.error(session_id)
        logger.error(str(e))
        s = create_session_with_context(context)
    return s


def get_current_conversation(**kwargs):
    try:
        return Conversation.objects.get(**kwargs)
    except Conversation.DoesNotExist:
        return None


def create_conversation(phone_number, session_id):
    conv, _ = Conversation.objects.get_or_create(phone_number=phone_number, session_id=session_id)
    return conv
