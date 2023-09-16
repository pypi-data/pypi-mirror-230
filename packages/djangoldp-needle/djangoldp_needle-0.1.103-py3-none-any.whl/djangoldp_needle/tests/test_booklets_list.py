from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from ..models import Booklet, BookletContributor


class TestBookletList(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_list_public_anonymous(self):
        self.store_booklet(public=True)

        response = self.client.get(
            "/booklets/",
            content_type='application/ld+json',
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_value['ldp:contains']), 1)

    def test_booklet_list_public_user_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet = self.store_booklet(public=True)
                self.store_booklet_contributor(booklet, user1, role[0])

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 1)

                transaction.savepoint_rollback(sid)

    def test_booklet_list_public_user_not_contributor(self):
        user1 = self.buildUser('user1')
        self.store_booklet(public=True)

        self.client.force_authenticate(user1)
        response = self.client.get(
            "/booklets/",
            content_type='application/ld+json',
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_value['ldp:contains']), 1)

    def test_booklet_list_private_anonymous(self):
        self.store_booklet(public=False)

        response = self.client.get(
            "/booklets/",
            content_type='application/ld+json',
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_value['ldp:contains']), 0)

    def test_booklet_list_private_not_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet(public=False)
                self.store_booklet_contributor(booklet, user2, role[0])

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 0)

                transaction.savepoint_rollback(sid)

    def test_booklet_list_private_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet = self.store_booklet(public=False)
                self.store_booklet_contributor(booklet, user1, role[0])

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 1)

                transaction.savepoint_rollback(sid)

    def store_booklet(self, public = False, collaboration = False):
        booklet = Booklet(
            title="title",
            abstract="",
            accessibility_public=public,
            collaboration_allowed=collaboration,
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
