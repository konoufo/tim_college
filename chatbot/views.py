# Create your views here.

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

# Create your views here.
account_sid = "AC2753af86e1e282a4ca4a79d40380e923"
auth_token = "859f7737020f3c55ddfa7e063a3b8867"
logger = logging.getLogger(__name__)


# Test simple sending
def send_sms(request):
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+15148139877",
        from_="+14387956005",
        body="Hello from Python!")

    print(message.sid)


@csrf_exempt
def inbound(request):
    body = request.POST.get('Body', None)
    logger.error(body)
    welcome = "Hi " + body + ", how can I help you?"
    twiml_response = MessagingResponse()
    twiml_response.message(welcome)
    return HttpResponse(twiml_response, content_type='application/xml')
