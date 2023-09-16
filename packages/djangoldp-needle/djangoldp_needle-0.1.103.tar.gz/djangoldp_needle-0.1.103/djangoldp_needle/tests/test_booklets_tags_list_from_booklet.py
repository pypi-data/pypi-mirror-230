from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from ..models import Booklet, BookletContributor, BookletTag


class TestBookletTagList(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_tags_list_public_anonymous(self):
        booklet = self.store_booklet(public=True)
        tag = self.store_booklet_tag(booklet=booklet, name='test')

        response = self.client.get(
            "/booklets/" + str(booklet.pk) + "/tags/",
            content_type='application/ld+json',
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_value['ldp:contains']), 1)

    def test_booklet_tags_list_private_anonymous(self):
        booklet = self.store_booklet(public=False)
        tag = self.store_booklet_tag(booklet=booklet, name='test')

        response = self.client.get(
            "/booklets/" + str(booklet.pk) + "/tags/",
            content_type='application/ld+json',
        )
        self.assertEqual(response.status_code, 404)

    def test_booklet_tags_list_public_anonymous_filter_booklet(self):
        booklet1 = self.store_booklet(public=True)
        booklet2 = self.store_booklet(public=True)
        self.store_booklet_tag(booklet=booklet1, name='test1')
        self.store_booklet_tag(booklet=booklet2, name='test2')

        response = self.client.get(
            "/booklets/" + str(booklet1.pk) + "/tags/",
            content_type='application/ld+json',
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_value['ldp:contains']), 1)

    def test_booklet_tags_list_public_user_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet1 = self.store_booklet(public=True)
                booklet2 = self.store_booklet(public=True)
                self.store_booklet_contributor(booklet1, user1, role[0])
                self.store_booklet_contributor(booklet2, user1, role[0])
                self.store_booklet_tag(booklet=booklet1, name='test')
                self.store_booklet_tag(booklet=booklet2, name='test')

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/" + str(booklet1.pk) + "/tags/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 1)

                transaction.savepoint_rollback(sid)

    def test_booklet_tags_list_public_user_not_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet1 = self.store_booklet(public=True)
                booklet2 = self.store_booklet(public=True)
                self.store_booklet_contributor(booklet2, user1, role[0])
                self.store_booklet_tag(booklet=booklet1, name='test')
                self.store_booklet_tag(booklet=booklet2, name='test')

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/" + str(booklet1.pk) + "/tags/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 1)

                transaction.savepoint_rollback(sid)

    def test_booklet_tags_list_private_user_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet1 = self.store_booklet(public=False)
                booklet2 = self.store_booklet(public=False)
                self.store_booklet_contributor(booklet1, user1, role[0])
                self.store_booklet_contributor(booklet2, user1, role[0])
                self.store_booklet_tag(booklet=booklet1, name='test')
                self.store_booklet_tag(booklet=booklet2, name='test')

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/" + str(booklet1.pk) + "/tags/",
                    content_type='application/ld+json',
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response_value['ldp:contains']), 1)

                transaction.savepoint_rollback(sid)

    def test_booklet_tags_list_private_user_not_contributor(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet1 = self.store_booklet(public=False)
                booklet2 = self.store_booklet(public=False)
                self.store_booklet_contributor(booklet2, user1, role[0])
                self.store_booklet_tag(booklet=booklet1, name='test')
                self.store_booklet_tag(booklet=booklet2, name='test')

                self.client.force_authenticate(user1)
                response = self.client.get(
                    "/booklets/" + str(booklet1.pk) + "/tags/",
                    content_type='application/ld+json',
                )
                self.assertEqual(response.status_code, 404)

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

    def store_booklet_tag(self, booklet, name):
        tag = BookletTag(
            booklet=booklet,
            name=name,
        )
        tag.save()

        return tag