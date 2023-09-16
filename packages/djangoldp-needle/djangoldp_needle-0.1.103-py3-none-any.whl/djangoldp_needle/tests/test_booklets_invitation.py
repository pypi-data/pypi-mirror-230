import requests_mock
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json
import datetime
from pkg_resources import resource_string

from ..models import Booklet, BookletContributor

from .data.target_url.realsites import real_sites

from .data.target_url.needlerealsites import needle_real_sites


class TestBookletInvitation(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_invitation_email_exist(self):
        for role in (BookletContributor.ROLE_OWNER, BookletContributor.ROLE_ADMIN):
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet()
                self.store_booklet_contributor(booklet, user1, role)

                self.client.force_authenticate(user1)
                response = self.client.post(
                    "/booklets/" + str(booklet.pk) + "/invitation/",
                    content_type='application/ld+json',
                    data=self._create_invitation_request('user2@test.startinblox.com')
                )
                self.assertEqual(response.status_code, 201)
                self.assertEqual(2, len(booklet.contributors.all()))
                self.assertEqual(user2, booklet.contributors.all()[1].user)

                transaction.savepoint_rollback(sid)

    def test_invitation_email_not_exist(self):
        for role in (BookletContributor.ROLE_OWNER, BookletContributor.ROLE_ADMIN):
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet()
                self.store_booklet_contributor(booklet, user1, role)

                self.client.force_authenticate(user1)
                response = self.client.post(
                    "/booklets/" + str(booklet.pk) + "/invitation/",
                    content_type='application/ld+json',
                    data=self._create_invitation_request('invalid@test.startinblox.com')
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(1, len(booklet.contributors.all()))

                transaction.savepoint_rollback(sid)

    def test_invitation_user_not_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        user3 = self.buildUser('user3')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user2)
        response = self.client.post(
            "/booklets/" + str(booklet.pk) + "/invitation/",
            content_type='application/ld+json',
            data=self._create_invitation_request('user3@test.startinblox.com')
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(2, len(booklet.contributors.all()))


    def store_booklet(self, owners, contributors, public = False, collaboration = False):
        booklet = Booklet(
            title="title",
            abstract="",
            accessibility_public=public,
            collaboration_allowed=collaboration,
            cover=1,
        )
        booklet.save()
        for owner in owners:
            booklet.owners.add(owner)
        for contributor in contributors:
            booklet.contributors.add(contributor)

        return booklet

    def _create_invitation_request(self, email):
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
            "email": email
        })

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