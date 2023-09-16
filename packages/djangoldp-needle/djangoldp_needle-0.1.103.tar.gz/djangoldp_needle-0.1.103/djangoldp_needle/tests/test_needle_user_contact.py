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

    def test_user_contact_add_valid(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        request_content = self.build_request("Test de message", "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontacts/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, NeedleUserContact.objects.count())
        new_contact = NeedleUserContact.objects.all()[0]
        # Validate generated UUID is valid
        uuid.UUID(new_contact.invitation_token)
        self.assertEqual("user2", new_contact.contact_to.username)
        self.assertEqual("user1", new_contact.contact_from.username)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('[Needle] Nouvelle demande de contact', mail.outbox[0].subject)
        self.assertEqual(['user2@test.startinblox.com'], mail.outbox[0].to)

        user1.refresh_from_db()
        expected = """Bonjour,

{} a souhaité vous inviter à rejoindre ses contacts sur Needle. Son adresse e-mail est {}.

Test de message

Pour accepter son invitation, veuillez suivre ce lien ou le copier-coller dans votre navigateur : {}/needleusercontact_validate/{}""".format(
            user1.avatar.get_full_name(),user1.email, settings.BASE_URL,
            new_contact.invitation_token,
        )
        result = mail.outbox[0].body
        self.assertEqual(expected, result)

    def test_user_contact_add_invalid_email(self):
        user1 = self.buildUser('user1')

        request_content = self.build_request("Test de message", "invalid")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/needleusercontacts/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual([
                             "Cette personne n'existe pas sur Needle. <solid-contact-button-add-invitation></solid-contact-button-add-invitation>"],
                         response.json()['E-mail'])

    def test_user_contact_add_existing(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        request_content = self.build_request("Test de message", "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        self.client.post(
            "/needleusercontacts/",
            content_type='application/ld+json',
            data=request_content
        )
        response = self.client.post(
            "/needleusercontacts/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(["Une invitation existe déjà pour cet utilisateur"],
                         response.json()['E-mail'])

    def test_user_contact_validate_invalid_token(self):
        response = self.client.get("/needleusercontact_validate/invalid")
        self.assertContains(response, 'Le lien que vous avez suivi est invalide ou expiré', status_code=404)

    def test_user_contact_validate_valid_token(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        new_contact = NeedleUserContact(contact_from=user1, contact_to=user2)
        new_contact.save()
        response = self.client.get("/needleusercontact_validate/" + str(new_contact.invitation_token))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, settings.INSTANCE_DEFAULT_CLIENT)

        new_contact.refresh_from_db()
        self.assertEqual(None, new_contact.invitation_token)
        reverse_contact = NeedleUserContact.objects.get(contact_from=user2, contact_to=user1)
        self.assertEqual(None, reverse_contact.invitation_token)

    def test_user_contact_validate_valid_token_existing_reverse(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        new_contact = NeedleUserContact(contact_from=user1, contact_to=user2)
        new_contact.save()
        reverse_contact = NeedleUserContact(contact_from=user2, contact_to=user1)
        reverse_contact.save()

        response = self.client.get("/needleusercontact_validate/" + str(new_contact.invitation_token))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, settings.INSTANCE_DEFAULT_CLIENT)

        new_contact.refresh_from_db()
        self.assertEqual(None, new_contact.invitation_token)
        reverse_contact.refresh_from_db()
        self.assertEqual(None, reverse_contact.invitation_token)

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
