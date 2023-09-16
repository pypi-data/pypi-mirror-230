import requests_mock
import uuid as uuid
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json, uuid
from pkg_resources import resource_string
from django.core import mail

from ..models import NeedleActivity, ContactMessage, NeedleUserContact, NeedleUserContactPending
from django.conf import settings

class TestNeedleUserContactPending(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_user_contact_pending_add_valid(self):
        user1 = self.buildUser('user1')

        request_content = self.build_request("Test de message", "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontactpending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, NeedleUserContactPending.objects.count())
        new_contact = NeedleUserContactPending.objects.all()[0]
        self.assertEqual("user2@test.startinblox.com", new_contact.contact_to_email)
        self.assertEqual("user1", new_contact.contact_from.username)

        user1.refresh_from_db()
        expected = """Bonjour,

{} a souhaité vous inviter à rejoindre ses contacts sur Needle. Son adresse e-mail est user1@test.startinblox.com .

Test de message

Pour accepter son invitation, veuillez suivre ce lien ou le copier-coller dans votre navigateur : {}/auth/register/""".format(
            user1.avatar.get_full_name(), settings.BASE_URL
        )
        result = mail.outbox[0].body
        self.assertEqual(expected, result)

    def test_user_contact_pending_add_invalid_email(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        request_content = self.build_request("Test de message", "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontactpending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(["Cette personne existe déjà sur Needle"], response.json()['E-mail'])

    def test_user_creation_with_pending_contact(self):
        user1 = self.buildUser('user1')

        request_content = self.build_request("Test de message", "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontactpending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)

        user2 = self.buildUser('user2')
        self.assertEqual(0, NeedleUserContactPending.objects.count())
        self.assertEqual(2, NeedleUserContact.objects.count())
        contact = NeedleUserContact.objects.first()
        self.assertEqual(user1, contact.contact_from)
        self.assertEqual(user2, contact.contact_to)
        self.assertEqual(None, contact.invitation_token)
        contact_reverse = NeedleUserContact.objects.last()
        self.assertEqual(user2, contact_reverse.contact_from)
        self.assertEqual(user1, contact_reverse.contact_to)
        self.assertEqual(None, contact_reverse.invitation_token)

    def build_request(self, message, contact_to):
        return json.dumps({
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
            "message": message,
            "contact_to_email": contact_to,
        })
