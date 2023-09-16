import uuid

import requests_mock
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json
from pkg_resources import resource_string
from django.core import mail
from django.conf import settings

from ..models import NeedleActivity, ContactMessage, UserMailChangeToken


class TestUserMailChangeToken(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_user_mail_change_validate_invalid_token(self):
        response = self.client.get("/usermailchangetoken_validate/invalid")
        self.assertContains(response, 'Le lien que vous avez suivi est invalide ou expiré', status_code=404)

    def test_user_mail_change_validate_valid_token(self):
        user1 = self.buildUser('user1')
        new_change = UserMailChangeToken(creator=user1, email='newemail@test.com')
        new_change.save()
        response = self.client.get("/usermailchangetoken_validate/" + str(new_change.token))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, settings.INSTANCE_DEFAULT_CLIENT)

        user1.refresh_from_db()
        self.assertEquals(0, UserMailChangeToken.objects.count())
        self.assertEqual('newemail@test.com', user1.email)
