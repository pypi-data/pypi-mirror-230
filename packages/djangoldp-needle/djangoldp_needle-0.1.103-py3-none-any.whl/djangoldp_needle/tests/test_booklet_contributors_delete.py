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

    def test_booklet_contributors_delete_as_non_contributor_of_booklet(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )
        response_decoded = json.loads(response.content)


        self.assertEqual(response.status_code, 400)
        self.assertEqual("L'utilisateur doit être contributeur au carnet", response_decoded[0])
        self.assertEqual(1, BookletContributor.objects.count())

    def test_booklet_contributors_delete_less_admin(self):
        for role in (BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR, BookletContributor.ROLE_MODERATOR):
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet()
                self.store_booklet_contributor(booklet, user1, role)
                contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

                self.client.force_authenticate(user1)
                response = self.client.delete(
                    "/bookletcontributors/" + str(contributor.pk) + '/'


                )
                response_decoded = json.loads(response.content)


                self.assertEqual(response.status_code, 400)
                self.assertEqual('L\'utilisateur doit être au moins administrateur du carnet',
                                 response_decoded[0])
                self.assertEqual(2, BookletContributor.objects.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_contributors_delete_other_as_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(1, BookletContributor.objects.count())

    def test_booklet_contributors_delete_other_as_admin(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(1, BookletContributor.objects.count())


    def test_booklet_contributors_delete_owner_other_as_admin(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_ADMIN)
        contributor = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_OWNER)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )
        response_decoded = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual('Impossible de modifier un propriétaire en étant admin',
                         response_decoded[0])
        self.assertEqual(2, BookletContributor.objects.count())

    def test_booklet_contributors_delete_own_as_owner_single_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )

        response_decoded = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Un propriétaire ne peux pas se supprimer d\'un carnet',
                         response_decoded[0])
        self.assertEqual(2, BookletContributor.objects.count())

    def test_booklet_contributors_delete_own_as_owner_multiple_owner(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_OWNER)

        self.client.force_authenticate(user1)
        response = self.client.delete(
            "/bookletcontributors/" + str(contributor.pk) + '/'

        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(1, BookletContributor.objects.count())

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