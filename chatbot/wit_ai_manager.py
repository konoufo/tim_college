import logging
from collections import OrderedDict

from django.conf import settings
from django import setup
from django.template.loader import render_to_string

from wit import Wit
from twilio.rest import Client

# when using standalone Interactive Mode, we need to configure Django manually
if not settings.configured:
    import os, sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    # sys.path.append(os.path.join(base_dir, 'tim'))
    os.environ["DJANGO_SETTINGS_MODULE"] = "tim.settings"
    print(settings.DEBUG)
    # Make project directory the current working directory.
    # os.chdir(base_dir)
    setup()
    print('setup done')
from .models import get_session, create_session, update_or_create_with_context, get_current_conversation

logger = logging.getLogger('chatbot.wit_ai_manager')

# Twilio
account_sid = "AC2753af86e1e282a4ca4a79d40380e923"
auth_token = "859f7737020f3c55ddfa7e063a3b8867"
account_phone = "+14387956005"
client_twilio = Client(account_sid, auth_token)

# Wit credentials
access_token = 'HYIAH4DQRFWM65BNI2SNQ2TPAM2ZGV7L'


def create_sms(to, body):
    message = client_twilio.messages.create(
        to=to,
        from_=account_phone,
        body=body)
    return message


def send_civilities(s):
    """ Send a message of introduction when necessary
    :param s: SessionStore object that contains current conversation
    :return: message sent if everything goes well. Otherwise `False`.
    """
    if s.get('hasIntroduced', None):
        logger.info('I can\'t just keep introducing myself. Remember the name !')
        return False
    s['hasIntroduced'] = True
    s.save()
    content = render_to_string('chatbot/civilities.txt', context={'context': s.get('context')})
    if s.get('phone_number', None) is not None:
        message = create_sms(s['phone_number'], content)
        logger.info('I sent my civilities to a phone number *chuckles*.')
        return message
    logger.info('I sent my civilities to a console terminal, *smh*.')
    print(str(content))
    return content


def send_follow_up(s):
    """ Send a complement to bot answer only when necessary
    :param s: SessionStore object that contains current conversation
    :return: message sent if everything goes well. Otherwise `False`.
    """
    logger.debug(s.items())
    if not s.get('resultCount') or not s['context'].get('result'):
        return False
    content = render_to_string('chatbot/follow_up.txt', context={'context': s.get('context')})
    if s.get('phone_number', None) is not None:
        message = create_sms(s['phone_number'], content)
        return message
    print(content)
    return content


def send(request, response):
    """ Sending bot answers to user in Interactive Mode
    :param request: a dict object containing the payload from the last chatbot action
    :param response: a dict object containing the bot answer
    :return: `None` if everything goes well. `False` otherwise.
    """
    try:
        s = get_session(request['session_id'])
    except KeyError:
        logger.error('session_id is missing from request in Interactive Mode. That\'s weird !')
        return False
    except Exception:
        s = create_session(request['session_id'])
    send_civilities(s)
    print(response['text'])
    send_follow_up(s)


def send_sms(request, response):
    """ Sending bot answers to user over Twilio SMS
        :param request: a dict object containing the payload from the last chatbot action
        :param response: a dict object containing the bot answer
        :return: message sent if everything goes well. `False` otherwise.
    """
    try:
        s = get_session(request['session_id'])
    except KeyError:
        logger.error('session_id is missing from request.')
        return False
    except Exception:
        conv = get_current_conversation(session_id=request['session_id'])
        s = conv.renew_session()
    send_civilities(s)
    message = create_sms(s['phone_number'], response['text'])
    send_follow_up(s)
    return message


# map of context and entities which influence our Bot decisions
factors = OrderedDict([('name', 'contact'), ('location', 'location'), ('career', 'career'),
                       ('money', 'amount_of_money')])


def retrieve_intelligence(request):
    context, entities, session_id = request['context'], request['entities'], request['session_id']
    return context, entities, session_id


def first_entity_value(entities, entity):
    """ Return first value captured for `entity`
    """
    if entities is None or (entity not in entities):
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def sanitize_post_result(context):
    """ Sanitize context from unnecessary keys after giving result
    """
    context.pop('result', None)
    return context


def sanitize_context(context):
    """ Sanitize context from unnecessary keys after every action
    """
    context = sanitize_post_result(context)
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


def compute_result(session):
    """ Return computed result every time we get all necessary information from user.
    :param session: current conversation SessionStore object
    :return: context payload with final result
    """
    context = session['context']  # `context` is a shallow copy of `session['context']`
    session['resultCount'] = session.get('resultCount', 0) + 1
    context.update({'result': render_to_string('chatbot/results.txt', {'context': context})})
    session.save()
    assert session['context'] == context
    return {'result': context['result'],
            'name': context['name']}


def start_conversation(request):
    """ Action triggered when entity `contact` is detected in received user message
    :param request: dict containing current state of conversation
    :return: new `context` dict
    """
    context = request['context']
    entities = request['entities']
    session_id = request['session_id']
    name = first_entity_value(entities, 'contact')
    greetings = first_entity_value(entities, 'greetings')
    s = update_or_create_with_context(session_id, context)
    context = s['context']
    if name:
        context['name'] = name
        context.pop('noName', None)
    else:
        if context.get('name') is None:
            context['noName'] = True
    s['context'].update(sanitize_context(context))
    return s['context']


def filter_by_location(request):
    """ Action triggered when intent `filterByLocation` is detected in received user message
    :param request: dict containing current state of conversation
    :return: new `context` dict
    """
    context, entities, session_id = retrieve_intelligence(request)
    location = first_entity_value(entities, 'location')
    s = update_or_create_with_context(session_id, context)
    context = s['context']
    if location:
        context['location'] = location
        context.pop('noLocation', None)
    elif context.get('location', None) is None:
        context['noLocation'] = True
    s['context'].update(sanitize_context(context))
    return s['context']


def filter_by_tuition(request):
    """ Action triggered when intent `filterByTuition` is detected in received user message
    :param request: dict containing current state of conversation
    :return: new `context` dict
    """
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
    s['context'].update(sanitize_context(context))
    logger.debug(s['context'])
    assert s['context'] == context
    if can_compute_result(context):
        return compute_result(s)
    return context


def find_university(request):
    """ Action triggered when intent `university` is detected in received user message
    :param request: dict containing current state of conversation
    :return: new `context` dict
    """
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
    s['context'].update(sanitize_context(context))
    logger.debug(context)
    assert s['context'] == context
    if can_compute_result(context):
        return compute_result(s)
    s.save()
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
