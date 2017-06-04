# -*- coding: utf-8 -*-
"""Wit.ai powered bot, TIM, capabilities

This module handles communication between incoming users and our wit.ai powered bot.
It contains methods that generate answers based off entities extracted from incoming messages.
These methods enable TIM to greet, ask for more information or deliver an orientation advice to the user
depending on the context.

Attributes:
    factors (OrderedDict): map of context (keys), we need, to entities (values), we extract.
    filters (dict): map of context (keys) to filtering methods (values) we apply to compute a definitive set
        of matching university programs.
"""

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
from .queries import find_study_program_by_search, empty_queryset

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
    else:
        conv = get_current_conversation(session_id=request['session_id'])
        s = conv.renew_session()
    send_civilities(s)
    message = create_sms(s['phone_number'], response['text'])
    send_follow_up(s)
    return message


factors = OrderedDict([('name', 'contact'), ('location', 'location'), ('career', 'career'),
                       ('money', 'zambian_money')])

filters = {
    'career': find_study_program_by_search
}


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


def filter_outcomes(session):
    """Filtrer les possibilités (programmes universitaires) qui correspondent aux données de la conversation

    Args:
        session (SessionStore) : contient toutes les données sur la conversation

    Returns:
        SessionStore: `session`. With resulting queryset in `session['queryset']`.
    """
    queryset = None
    for resource in factors.keys():
        try:
            disjoint_queryset = filters[resource](session['context'][resource])
        except KeyError:
            continue
        try:
            queryset.union(disjoint_queryset)
        except AttributeError:
            queryset = disjoint_queryset
    session['queryset'] = list(queryset or [])
    return session


def renew_context(context, entities, resource=None, resources=None):
    """ Updates context based off new extracted entities

    Args:
        context (dict): current state of conversation represented by predefined elements of context and their values.
        entities (dict): entities extracted by wit.ai NLP algorithms
        resource (str): optional. Only element of context to update
        resources (iterable): optional. Only elements of context to update

    Returns:
        Updated `context`.
    """
    if resource is not None:
        _factors = OrderedDict([(resource, factors[resource])])
    elif resources is not None:
        _factors = OrderedDict([(resource, factors[resource]) for resource in resources])
    else:
        _factors = factors
    for resource, entity in _factors.items():
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
    return context


def sanitize_context_post_result(context):
    """ Sanitize context from unnecessary keys after giving result
    """
    context.pop('result', None)
    return context


def sanitize_context(context):
    """ Sanitize context from unnecessary keys after every action
    """
    context = sanitize_context_post_result(context)
    for resource in factors.keys():
        anti_resource = 'no{}'.format(resource.capitalize())
        if anti_resource in context.keys():
            if resource in context.keys():
                context.pop(anti_resource, None)
    return context


def retrieve_session(request, resource=None):
    """ Retrieves session updated with new extracted entities

    Args:
        request: contains response from the bot brain (wit.ai)
        resource (str): optional. Only context element to update

    Returns:
        Updated session
    """
    context, entities, session_id = retrieve_intelligence(request)
    s = update_or_create_with_context(session_id, context)
    context = sanitize_context(renew_context(s['context'], entities, resource=resource))
    logger.debug(context)
    return s


def can_compute_result(context):
    for resource in factors.keys():
        if 'no{}'.format(resource.capitalize()) in context.keys():
            return False
    return True


def compute_result(session):
    """ Return computed result every time we get all necessary information from user.
    :param SessionStore session: current conversation SessionStore object
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
    :param dict request: contains current state of conversation as received from wit.ai
    :return: renewed `context` dict
    """
    s = retrieve_session(request, 'name')
    filter_outcomes(s).save()
    if can_compute_result(s['context']):
        return compute_result(s)
    return s['context']


def filter_by_location(request):
    """ Action triggered when intent `filterByLocation` is detected in received user message
    :param dict request: contains current state of conversation
    :return: renewed `context` dict
    """
    s = retrieve_session(request, resource='location')
    filter_outcomes(s).save()
    if can_compute_result(s['context']):
        return compute_result(s)
    return s['context']


def filter_by_tuition(request):
    """ Action triggered when intent `filterByTuition` is detected in received user message
    :param dict request: contains current state of conversation
    :return: new `context` dict
    """
    s = retrieve_session(request, resource='money')
    filter_outcomes(s).save()
    if can_compute_result(s['context']):
        return compute_result(s)
    return s['context']


def find_university(request):
    """ Action triggered when intent `university` is detected in received user message
    :param dict request: contains current state of conversation
    :return dict context: renewed `context`
    """
    s = retrieve_session(request)
    filter_outcomes(s).save()
    if can_compute_result(s['context']):
        return compute_result(s)
    return s['context']


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
