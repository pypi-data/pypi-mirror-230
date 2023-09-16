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


class TestBookletContributorPatch(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_contributors_change_role_as_non_contributor_of_booklet(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_ADMIN)
        )
        response_decoded = json.loads(response.content)

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual("L'utilisateur doit être contributeur au carnet", response_decoded['non_field_errors'][0])
        self.assertEqual(BookletContributor.ROLE_VISIT, contributor.role)

    def test_booklet_contributors_change_role_less_admin(self):
        for role in (BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR, BookletContributor.ROLE_MODERATOR):
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet()
                self.store_booklet_contributor(booklet, user1, role)
                contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/bookletcontributors/" + str(contributor.pk) + '/',
                    content_type='application/ld+json',
                    data=self.build_request(BookletContributor.ROLE_ADMIN)
                )
                response_decoded = json.loads(response.content)

                contributor.refresh_from_db()
                self.assertEqual(response.status_code, 400)
                self.assertEqual('L\'utilisateur doit être au moins administrateur du carnet',
                                 response_decoded['non_field_errors'][0])
                self.assertEqual(BookletContributor.ROLE_VISIT, contributor.role)

                transaction.savepoint_rollback(sid)

    def test_booklet_contributors_change_role_other_as_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_ADMIN)
        )

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BookletContributor.ROLE_ADMIN, contributor.role)

    def test_booklet_contributors_change_role_other_as_admin(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_ADMIN)
        )

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BookletContributor.ROLE_ADMIN, contributor.role)

    def test_booklet_contributors_remove_owner_other_as_admin(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_OWNER)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_VISIT)
        )
        response_decoded = json.loads(response.content)

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Impossible de modifier un propriétaire en étant admin',
                         response_decoded['non_field_errors'][0])
        self.assertEqual(BookletContributor.ROLE_OWNER, contributor.role)

    def test_booklet_contributors_add_owner_other_as_admin(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_OWNER)
        )
        response_decoded = json.loads(response.content)

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Impossible d\'ajouter un propriétaire en étant admin',
                         response_decoded['non_field_errors'][0])
        self.assertEqual(BookletContributor.ROLE_VISIT, contributor.role)

    def test_booklet_contributors_change_role_own_as_owner_single_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_ADMIN)
        )

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BookletContributor.ROLE_OWNER, contributor.role)

    def test_booklet_contributors_change_role_own_as_owner_multiple_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_OWNER)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/bookletcontributors/" + str(contributor.pk) + '/',
            content_type='application/ld+json',
            data=self.build_request(BookletContributor.ROLE_ADMIN)
        )

        contributor.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BookletContributor.ROLE_ADMIN, contributor.role)

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

    def build_request(self, role):
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