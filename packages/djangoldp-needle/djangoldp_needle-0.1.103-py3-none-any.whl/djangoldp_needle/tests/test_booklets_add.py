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


class TestBookletAdd(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_create(self):
        user1 = self.buildUser('user1')
        self.client.force_authenticate(user1)

        response = self.client.post(
            "/booklets/",
            content_type='application/ld+json',
            data=self._create_booklet('test')
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, Booklet.objects.count())

        booklet = Booklet.objects.first()
        self.assertEqual(1, booklet.contributors.count())

        contributor = booklet.contributors.first()
        self.assertEqual(BookletContributor.ROLE_OWNER, contributor.role)
        self.assertEqual(user1, contributor.user)


    def _create_booklet(self, title):
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
            "title": title,
            "abstract": "",
            "accessibility_public": False,
            "collaboration_allowed": False,
            "cover": 1
        })