import requests_mock
import uuid as uuid
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json, uuid
from pkg_resources import resource_string
from django.core import mail

from ..models import NeedleActivity, ContactMessage, NeedleUserContact, BookletContributorPending, BookletContributor, \
    Booklet
from django.conf import settings


class TestBookletContributorPending(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_contributor_pending_add_valid(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)

        request_content = self.build_request(booklet, "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributorspending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, BookletContributorPending.objects.count())
        new_contact = BookletContributorPending.objects.all()[0]
        self.assertEqual("user2@test.startinblox.com", new_contact.booklet_to_email)
        self.assertEqual(booklet, new_contact.booklet_from)

        user1.refresh_from_db()
        self.assertEqual(
            """{} veut vous inviter à contributer à son carnet title sur Needle.

Pour créer un compte, veuillez suivre ce lien ou le copier-coller dans votre navigateur : {}/auth/register/""".format(
                user1.avatar.get_full_name(), settings.BASE_URL
            ),
            mail.outbox[0].body
        )

    def test_booklet_contributor_pending_add_invalid_email(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)

        request_content = self.build_request(booklet, "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributorspending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(["Cette personne existe déjà sur Needle"], response.json()['E-mail'])

    def test_booklet_contributor_pending_non_owner(self):
        user1 = self.buildUser('user1')

        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)

        request_content = self.build_request(booklet, "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributorspending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(["Vous devez être propriétaire du carnet"], response.json()['Booklet'])

    def test_user_creation_with_pending_contributor(self):
        user1 = self.buildUser('user1')

        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)

        request_content = self.build_request(booklet, "user2@test.startinblox.com")

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributorspending/",
            content_type='application/ld+json',
            data=request_content
        )

        self.assertEqual(response.status_code, 201)

        user2 = self.buildUser('user2')
        self.assertEqual(0, BookletContributorPending.objects.count())
        self.assertEqual(2, BookletContributor.objects.count())
        contributor = BookletContributor.objects.last()
        self.assertEqual(booklet, contributor.booklet)
        self.assertEqual(user2, contributor.user)
        self.assertEqual(BookletContributor.ROLE_VISIT, contributor.role)

    def store_booklet(self):
        booklet = Booklet(
            title="title",
            abstract="",
            accessibility_public=False,
            collaboration_allowed=False,
            cover=1,
        )
        booklet.save()

        return booklet

    def store_booklet_contributor(self, booklet, user, role):
        contributor = BookletContributor(
            booklet=booklet,
            user=user,
            role=role
        )
        contributor.save()

        return contributor

    def build_request(self, booklet, contact_to):
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
            "booklet_from": {
                "@id": booklet.urlid
            },
            "booklet_to_email": contact_to,
        })
