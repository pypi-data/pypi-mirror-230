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


class TestBookletContributorPost(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_contributors_add_self_public_visitor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(True)

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributors/",
            content_type='application/ld+json',
            data=self.build_request(booklet, user1, BookletContributor.ROLE_VISIT)
        )

        self.assertEqual(response.status_code, 201)
        contributors = BookletContributor.objects.all()
        self.assertEqual(1, len(contributors))
        self.assertEqual(user1, contributors[0].user)
        self.assertEqual(booklet, contributors[0].booklet)
        self.assertEqual(BookletContributor.ROLE_VISIT, contributors[0].role)

    def test_booklet_contributors_add_self_non_public_visitor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(False)

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributors/",
            content_type='application/ld+json',
            data=self.build_request(booklet, user1, BookletContributor.ROLE_VISIT)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(0, BookletContributor.objects.count())

    def test_booklet_contributors_add_self_public_non_visitor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(True)

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/bookletcontributors/",
            content_type='application/ld+json',
            data=self.build_request(booklet, user1, BookletContributor.ROLE_CONTRIBUTOR)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(0, BookletContributor.objects.count())

    def test_booklet_contributors_add_other_user_public_visitor(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet(True)

        self.client.force_authenticate(user2)
        response = self.client.post(
            "/bookletcontributors/",
            content_type='application/ld+json',
            data=self.build_request(booklet, user1, BookletContributor.ROLE_VISIT)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(0, BookletContributor.objects.count())

    def test_booklet_contributors_admin_add_other_user_visit(self):
        for role in [BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
            for public in [True, False]:
                with transaction.atomic():
                    sid = transaction.savepoint()

                    user1 = self.buildUser('user1')
                    user2 = self.buildUser('user2')
                    booklet = self.store_booklet(public)
                    booklet_contributor = self.store_booklet_contributor(booklet, user1, role)

                    self.client.force_authenticate(user1)
                    response = self.client.post(
                        "/bookletcontributors/",
                        content_type='application/ld+json',
                        data=self.build_request(booklet, user2, BookletContributor.ROLE_VISIT)
                    )

                    self.assertEqual(response.status_code, 201)
                    contributors = BookletContributor.objects.all()
                    self.assertEqual(2, len(contributors))
                    self.assertEqual(user2, contributors[1].user)
                    self.assertEqual(booklet, contributors[1].booklet)
                    self.assertEqual(BookletContributor.ROLE_VISIT, contributors[1].role)

                    transaction.savepoint_rollback(sid)

    def test_booklet_contributors_admin_add_other_user_non_visit(self):
        for role in [BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
            for public in [True, False]:
                with transaction.atomic():
                    sid = transaction.savepoint()

                    user1 = self.buildUser('user1')
                    user2 = self.buildUser('user2')
                    booklet = self.store_booklet(public)
                    booklet_contributor = self.store_booklet_contributor(booklet, user1, role)

                    self.client.force_authenticate(user1)
                    response = self.client.post(
                        "/bookletcontributors/",
                        content_type='application/ld+json',
                        data=self.build_request(booklet, user2, BookletContributor.ROLE_MODERATOR)
                    )

                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(1, BookletContributor.objects.count())

                    transaction.savepoint_rollback(sid)

        def test_booklet_contributors_non_admin_add_other_user_visit(self):
            for role in [BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR, BookletContributor.ROLE_MODERATOR]:
                for public in [True, False]:
                    with transaction.atomic():
                        sid = transaction.savepoint()

                        user1 = self.buildUser('user1')
                        user2 = self.buildUser('user2')
                        booklet = self.store_booklet(public)
                        booklet_contributor = self.store_booklet_contributor(booklet, user1, role)

                        self.client.force_authenticate(user1)
                        response = self.client.post(
                            "/bookletcontributors/",
                            content_type='application/ld+json',
                            data=self.build_request(booklet, user2, BookletContributor.ROLE_VISIT)
                        )

                        self.assertEqual(response.status_code, 403)
                        self.assertEqual(1, BookletContributor.objects.count())

                        transaction.savepoint_rollback(sid)

    def store_booklet(self, public):
        booklet = Booklet(
            title="title",
            abstract="",
            accessibility_public=public,
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

    def build_request(self, booklet, user, role):
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
            "role": role,
            "booklet": {
                "@id": booklet.urlid,
            },
            "user": {
                "@id": user.urlid,
            },
        })

    def store_booklet_contributor(self, booklet, user, role):
        contributor = BookletContributor(
            booklet=booklet,
            user=user,
            role=role
        )
        contributor.save()

        return contributor