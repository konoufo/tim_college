import logging

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from django.shortcuts import render
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt

from wit import Wit

from chatbot.models import get_current_conversation, create_conversation, create_session_with_number, get_session, \
    update_session_with_context
# from .queries import *


class ChatDemoView(View):
    def get(self, request):
        return render(request, 'chatdemo.html')


# Twilio credentials
account_sid = "AC2753af86e1e282a4ca4a79d40380e923"
auth_token = "859f7737020f3c55ddfa7e063a3b8867"
logger = logging.getLogger(__name__)

# Wit credentials
access_token = 'HYIAH4DQRFWM65BNI2SNQ2TPAM2ZGV7L'


# Send function for Wit Actions
def send_sms(request, response):
    client_twilio = Client(account_sid, auth_token)
    try:
        s = get_session(request['session_id'])
    except KeyError:
        print('session_id is missing')
        return None
    message = client_twilio.messages.create(
        to=s['phone_number'],
        from_="+14387956005",
        body=response['text'])
    logger.error(request.POST.get('From', None))
    return message


@csrf_exempt
def inbound(request):
    message = request.POST.get('Body', None)
    user_number = request.POST.get('From', None)
    conversation = get_current_conversation(user_number)
    try:
        s = get_session(conversation.session_id)
    except AttributeError:
        s = create_session_with_number(user_number)
        create_conversation(user_number, s.session_key)
    logger.error(user_number)
    session_id = s.session_key
    s['context'] = s.get('context', {})
    s['context'].update(client_wit.run_actions(session_id, message, s['context']))
    s.save()
    return None


# Wit.ai intent functions

def send(request, response):
    print(response['text'])


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def start_conversation(request):
    context = request['context']
    entities = request['entities']
    session_id = request['session_id']
    name = first_entity_value(entities, 'contact')
    greetings = first_entity_value(entities, 'greetings')
    if greetings:
        if name:
            context['name'] = name
            if context.get('noName') is not None:
                del context['noName']
        else:
            context['noName'] = True
            if context.get('name') is not None:
                del context['name']
    s = update_session_with_context(session_id, context)
    return s['context']


def filter_by_location(request):
    context = request['context']
    entities = request['entities']
    session_id = request['session_id']
    location = first_entity_value(entities, 'location')
    if location:
        context['location'] = location
    s = update_session_with_context(session_id, context)
    return s['context']

actions = {
    'send': send_sms,
    'startConversation': start_conversation,
    'filterByLocation': filter_by_location,
}

client_wit = Wit(access_token=access_token, actions=actions)
# client_wit.interactive()
