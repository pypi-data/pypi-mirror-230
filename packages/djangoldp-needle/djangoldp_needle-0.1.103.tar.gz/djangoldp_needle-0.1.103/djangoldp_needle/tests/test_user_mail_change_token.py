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

    def test_user_mail_change_token(self):
        user1 = self.buildUser('user1')

        request_content = json.dumps({
            "@context": {"@vocab": "http://happy-dev.fr/owl/#",
                         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#",
                         "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label",
                         "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl",
                         "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat": "geo:lat",
                         "lng": "geo:long", "entrepreneurProfile": "http://happy-dev.fr/owl/#entrepreneur_profile",
                         "mentorProfile": "http://happy-dev.fr/owl/#mentor_profile", "account": "hd:account",
                         "messageSet": "http://happy-dev.fr/owl/#message_set",
                         "author": "http://happy-dev.fr/owl/#author_user",
                         "title": "http://happy-dev.fr/owl/#title"},
            "email": "newmail@test.com",
        })

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/usermailchangetokens/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)
        change_tokens = UserMailChangeToken.objects.all()
        # Validate generated UUID is valid
        uuid.UUID(change_tokens[0].token)

        self.assertEqual(1, len(change_tokens))
        self.assertEqual("user1", change_tokens[0].creator.username)
        self.assertEqual("newmail@test.com", change_tokens[0].email)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('[Needle] Changement de mail', mail.outbox[0].subject)
        self.assertEqual(['newmail@test.com'], mail.outbox[0].to)
        self.assertEqual(
            """Bonjour {},

Pour valider votre nouveau mail sur Needle, veuillez suivre ce lien ou le copier-coller dans votre navigateur : {}/usermailchangetoken_validate/{}"""
            .format(change_tokens[0].creator.avatar.get_full_name(), settings.BASE_URL, change_tokens[0].token),
            mail.outbox[0].body
        )

