import logging
from collections import OrderedDict

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
from .models import get_session, update_or_create_with_context, get_current_conversation

logger = logging.getLogger('chatbot.wit_ai_manager')

# Twilio credentials
account_sid = "AC2753af86e1e282a4ca4a79d40380e923"
auth_token = "859f7737020f3c55ddfa7e063a3b8867"


# Wit credentials
access_token = 'HYIAH4DQRFWM65BNI2SNQ2TPAM2ZGV7L'


# Wit.ai intent functions
def send(request, response):
    print(response['text'])


# Sender function to speak to Wit Chatbot over Twilio SMS
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
    except Exception:
        conv = get_current_conversation(session_id=request['session_id'])
        s = {'phone_number': conv.phone_number}
    message = client_twilio.messages.create(
        to=s['phone_number'],
        from_="+14387956005",
        body=response['text'])
    return message


# mapping context and entities that influence our Bot decisions
factors = OrderedDict([('name', 'contact'), ('location', 'location'), ('career', 'career'),
                       ('money', 'amount_of_money')])


def retrieve_intelligence(request):
    context, entities, session_id = request['context'], request['entities'], request['session_id']
    return context, entities, session_id


def first_entity_value(entities, entity):
    if entities is None or (entity not in entities):
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def sanitize_context(context):
    for resource in factors.keys():
        anti_resource = 'no{}'.format(resource.capitalize())
        if anti_resource in context.keys():
            if resource in context.keys():
                context.pop(anti_resource, None)
    return context


def can_compute_result(context):
    for resource in factors.keys():
        if 'no{}'.format(resource.capitalize()) in context.keys():
            return False
    return True


def compute_result(context):
    return {'result': 'You should probably go to UNZA. Though I\'m still learning myself, so i\'m not sure yet' +
                      ' if it\'' +
                      's a godd advice. I think they offer a few programs in {} studies.'.format(context['career']),
            'name': context.get('name')}


def start_conversation(request):
    context = request['context']
    entities = request['entities']
    session_id = request['session_id']
    name = first_entity_value(entities, 'contact')
    greetings = first_entity_value(entities, 'greetings')
    if name:
        context['name'] = name
        context.pop('noName', None)
    else:
        if context.get('name') is None:
            context['noName'] = True
    s = update_or_create_with_context(session_id, context)
    return s['context']


def filter_by_location(request):
    context, entities, session_id = retrieve_intelligence(request)
    location = first_entity_value(entities, 'location')
    if location:
        context['location'] = location
        context.pop('noLocation', None)
    s = update_or_create_with_context(session_id, context)
    return s['context']


def filter_by_tuition(request):
    context, entities, session_id = retrieve_intelligence(request)
    value = first_entity_value(entities, 'amount_of_money') or first_entity_value(entities, 'zambian_money')
    s = update_or_create_with_context(session_id, context)
    context = s['context']
    if value is None:
        if context.get('money', None) is None:
            context['noMoney'] = True
    else:
        context.update({'money': value})
        context.pop('noMoney', None)
    s.save()
    logger.debug(s['context'])
    assert s['context'] == context
    if can_compute_result(context):
        return compute_result(context)
    return context


def find_university(request):
    context, entities, session_id = retrieve_intelligence(request)
    s = update_or_create_with_context(session_id, context)
    context = s['context']
    for resource, entity in factors.items():
        value = first_entity_value(entities, entity)
        if value is None:
            if context.get(resource, None) is None:
                context['no{}'.format(resource.capitalize())] = True
                break
        else:
            if resource == 'name' and context.get('name', None) is not None:
                continue
            context.update({resource: value})
            context.pop('no{}'.format(resource.capitalize()), None)
    context = sanitize_context(context)
    logger.debug(context)
    assert s['context'] == context
    s.save()
    if can_compute_result(context):
        return compute_result(context)
    return context


actions = {
    'send': send_sms,
    'startConversation': start_conversation,
    'filterByLocation': filter_by_location,
    'findUniversity': find_university,
    'filterByTuition': filter_by_tuition,
}

client_wit = Wit(access_token=access_token, actions=actions)
# Run with python3 -m chatbot.wit_ai_manager
if __name__ == "__main__":
    actions.update({'send': send})
    client_wit.interactive()
