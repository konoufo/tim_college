import os

from django.conf import settings
import django

from wit import Wit
from twilio.rest import Client

if not settings.configured:
    import os, sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    # sys.path.append(os.path.join(base_dir, 'tim'))
    os.environ["DJANGO_SETTINGS_MODULE"] = "tim.settings"
    print(settings.DEBUG)
    # Make project directory the current working directory.
    # os.chdir(base_dir)
    # This is so models get loaded. I don't know why django.setup() is not working.
    django.setup()
    print('setup done')
from .models import update_session_with_context, get_session, create_session_with_context


# Twilio credentials
account_sid = "AC2753af86e1e282a4ca4a79d40380e923"
auth_token = "859f7737020f3c55ddfa7e063a3b8867"


# Wit credentials
access_token = 'HYIAH4DQRFWM65BNI2SNQ2TPAM2ZGV7L'


# Wit.ai intent functions
def send(request, response):
    print(response['text'])


# Send function for Wit Actions
def send_sms(request, response):
    client_twilio = Client(account_sid, auth_token)
    try:
        s = get_session(request['session_id'])
    except KeyError:
        print('session_id is missing')
        return None
    except IndexError:
        print('session does not exist')
        return None
    message = client_twilio.messages.create(
        to=s['phone_number'],
        from_="+14387956005",
        body=response['text'])
    return message


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
    try:
        s = update_session_with_context(session_id, context)
    except IndexError:
        s = create_session_with_context(context)
    return s['context']


def filter_by_location(request):
    context = request['context']
    entities = request['entities']
    session_id = request['session_id']
    location = first_entity_value(entities, 'location')
    if location:
        context['location'] = location
    try:
        s = update_session_with_context(session_id, context)
    except IndexError:
        s = create_session_with_context(context)
    return s['context']

actions = {
    'send': send_sms,
    'startConversation': start_conversation,
    'filterByLocation': filter_by_location,
}

client_wit = Wit(access_token=access_token, actions=actions)

if __name__ == "__main__":
    actions.update({'send': send})
    client_wit.interactive()
