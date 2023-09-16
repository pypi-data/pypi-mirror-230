import requests_mock
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json
from pkg_resources import resource_string
from django.core import mail

from ..models import NeedleActivity, ContactMessage


class TestUserContact(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_user_contact(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

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
            "message": "Test de message",
            "target": {
                "@id": user2.urlid
            },
            "source": {
                "@id": user1.urlid
            }
        })

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/contact_messages/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, ContactMessage.objects.count())
        self.assertEqual("user2", ContactMessage.objects.all()[0].target.username)
        self.assertEqual("user1", ContactMessage.objects.all()[0].source.username)
        self.assertEqual("Test de message", ContactMessage.objects.all()[0].message)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('[Needle] Nouveau message', mail.outbox[0].subject)
        self.assertEqual(['user2@test.startinblox.com'], mail.outbox[0].to)
        self.assertEqual(
            """Bonjour,

Vous avez recu un nouveau message sur Needle de user1@test.startinblox.com :
Test de message

""",
            mail.outbox[0].body
        )

