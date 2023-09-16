from django.conf import settings
from django.core.mail import send_mail
from djangoldp.views import JSONLDParser, NoCSRFAuthentication, LDPViewSet
from djangoldp_account.models import LDPUser
from rest_framework.exceptions import ValidationError
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.template import loader

class ContactMessageView(LDPViewSet):
    pass
