from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from ..models import Booklet, BookletContributor, BookletTag, BookletTagTarget


class TestBookletTagGet(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_tags_get_public_anonymous(self):
        booklet = self.store_booklet(public=True)
        tag = self.store_booklet_tag(booklet=booklet, name='test')
        tag_target = self.store_booklet_tag_target(tag=tag, target='target')

        response = self.client.get(
            "/booklettagtargets/" + str(tag_target.pk) + "/",
            content_type='application/ld+json',
        )
        self.assertEqual(response.status_code, 200)

    def test_booklet_tags_get_private_anonymous(self):
        booklet = self.store_booklet(public=False)
        tag = self.store_booklet_tag(booklet=booklet, name='test')
        tag_target = self.store_booklet_tag_target(tag=tag, target='target')

        response = self.client.get(
            "/booklettagtargets/" + str(tag_target.pk) + "/",
            content_type='application/ld+json',
        )
        self.assertEqual(response.status_code, 404)

    def test_booklet_tags_get_user_contributor(self):
        for public in [True, False]:
            for role in BookletContributor.ROLE_CHOICES:
                with transaction.atomic():
                    sid = transaction.savepoint()

                    user1 = self.buildUser('user1')
                    booklet = self.store_booklet(public=public)
                    self.store_booklet_contributor(booklet, user1, role)
                    tag = self.store_booklet_tag(booklet=booklet, name='test')
                    tag_target = self.store_booklet_tag_target(tag=tag, target='target')

                    self.client.force_authenticate(user1)
                    response = self.client.get(
                        "/booklettagtargets/" + str(tag_target.pk) + "/",
                        content_type='application/ld+json',
                    )
                    self.assertEqual(response.status_code, 200)

                    transaction.savepoint_rollback(sid)

    def test_booklet_tags_get_public_user_not_contributor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(public=True)
        tag = self.store_booklet_tag(booklet=booklet, name='test')
        tag_target = self.store_booklet_tag_target(tag=tag, target='target')

        self.client.force_authenticate(user1)
        response = self.client.get(
            "/booklettagtargets/" + str(tag_target.pk) + "/",
            content_type='application/ld+json',
        )
        self.assertEqual(response.status_code, 200)

    def test_booklet_tags_get_private_user_not_contributor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(public=False)
        tag = self.store_booklet_tag(booklet=booklet, name='test')
        tag_target = self.store_booklet_tag_target(tag=tag, target='target')

        self.client.force_authenticate(user1)
        response = self.client.get(
            "/booklettagtargets/" + str(tag_target.pk) + "/",
            content_type='application/ld+json',
        )
        self.assertEqual(response.status_code, 404)

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

    def store_booklet_tag_target(self, tag, target):
        tagtarget = BookletTagTarget(
            tag=tag,
            target=target,
        )
        tagtarget.save()

        return tagtarget