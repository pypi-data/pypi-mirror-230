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


class TestBookletList(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_quit_as_contributor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1)
        self.client.force_authenticate(user1)

        response = self.client.post(
            "/booklets/" + str(booklet.pk) + "/quit/",
            content_type='application/ld+json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(booklet.contributors.count(), 0)

    def test_booklet_quit_as_not_contributor(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user2)
        self.client.force_authenticate(user1)

        response = self.client.post(
            "/booklets/" + str(booklet.pk) + "/quit/",
            content_type='application/ld+json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(booklet.contributors.count(), 1)

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

    def store_booklet_contributor(self, booklet, user):
        contributor = BookletContributor(
            booklet=booklet,
            user=user,
            role=BookletContributor.ROLE_VISIT
        )
        contributor.save()

        return contributor
