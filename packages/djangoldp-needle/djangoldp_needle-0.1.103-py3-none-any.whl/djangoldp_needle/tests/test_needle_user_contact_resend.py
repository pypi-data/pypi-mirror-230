import requests_mock
import uuid as uuid
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json, uuid
from pkg_resources import resource_string
from django.core import mail

from ..models import NeedleActivity, ContactMessage, NeedleUserContact
from django.conf import settings


class TestNeedleUserContact(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_user_contact_resend_success(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        contact = NeedleUserContact(contact_from=user1, contact_to=user2, message='test de contenu')
        contact.save()

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontact/" + str(contact.pk) + "/resend/",
            content_type='application/ld+json',
            data=self.build_request()
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(1, NeedleUserContact.objects.count())

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('[Needle] Nouvelle demande de contact', mail.outbox[0].subject)
        self.assertEqual(['user2@test.startinblox.com'], mail.outbox[0].to)

        user1.refresh_from_db()
        expected = """Bonjour,

{} a souhaité vous inviter à rejoindre ses contacts sur Needle. Son adresse e-mail est  .

test de contenu

Pour accepter son invitation, veuillez suivre ce lien ou le copier-coller dans votre navigateur : {}/needleusercontact_validate/{}""".format(
            user1.avatar.get_full_name(), settings.BASE_URL,
            contact.invitation_token,
        )
        result = mail.outbox[0].body
        self.assertEqual(expected, result)

    def test_user_contact_resend_invalid_user(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        contact = NeedleUserContact(contact_from=user1, contact_to=user2, message='test de contenu')
        contact.save()

        self.client.force_authenticate(user2)
        response = self.client.post(
            "/needleusercontact/" + str(contact.pk) + "/resend/",
            content_type='application/ld+json',
            data=self.build_request()
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_contact_resend_no_token(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        contact = NeedleUserContact(contact_from=user1, contact_to=user2, message='test de contenu')
        contact.save()
        contact.invitation_token = None
        contact.save()

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontact/" + str(contact.pk) + "/resend/",
            content_type='application/ld+json',
            data=self.build_request()
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)

    def build_request(self):
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
        })
