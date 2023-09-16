import json

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

    def test_booklet_tags_add_public_anonymous(self):
        booklet = self.store_booklet(public=True)
        tag = self.store_booklet_tag(booklet=booklet, name='test1')

        response = self.client.post(
            "/booklettagtargets/",
            content_type='application/ld+json',
            data=self.build_request(tag, 'test')
        )
        self.assertEqual(response.status_code, 403)

    def test_booklet_tags_add_public_authenticated_not_contributor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet(public=True)

        booklet2 = self.store_booklet(public=True)
        self.store_booklet_contributor(booklet2, user1, BookletContributor.ROLE_ADMIN)

        tag = self.store_booklet_tag(booklet=booklet, name='test1')
        tag2 = self.store_booklet_tag(booklet=booklet2, name='test2')

        self.client.force_authenticate(user1)
        response = self.client.post(
            "/booklettagtargets/",
            content_type='application/ld+json',
            data=self.build_request(tag, 'test')
        )
        self.assertEqual(response.status_code, 403)

    def test_booklet_tags_add_authenticated_contributor_not_moderator(self):
        for public in [True, False]:
            for role in [BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR]:
                with transaction.atomic():
                    sid = transaction.savepoint()

                    user1 = self.buildUser('user1')
                    booklet = self.store_booklet(public=public)
                    self.store_booklet_contributor(booklet, user1, role)
                    tag = self.store_booklet_tag(booklet=booklet, name='test1')

                    self.client.force_authenticate(user1)
                    response = self.client.post(
                        "/booklettagtargets/",
                        content_type='application/ld+json',
                        data=self.build_request(tag, 'test')
                    )
                    self.assertEqual(response.status_code, 403)

                    transaction.savepoint_rollback(sid)

    def test_booklet_tags_add_authenticated_contributor_moderator(self):
        for public in [True, False]:
            for role in [BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
                with transaction.atomic():
                    sid = transaction.savepoint()

                    user1 = self.buildUser('user1')
                    booklet = self.store_booklet(public=public)
                    self.store_booklet_contributor(booklet, user1, role)
                    tag = self.store_booklet_tag(booklet=booklet, name='test1')

                    self.client.force_authenticate(user1)
                    response = self.client.post(
                        "/booklettagtargets/",
                        content_type='application/ld+json',
                        data=self.build_request(tag, 'test')
                    )
                    self.assertEqual(response.status_code, 201)
                    tags = BookletTag.objects.all()
                    self.assertEqual(1, len(tags))
                    self.assertEqual(booklet, tags[0].booklet)
                    self.assertEqual('test1', tags[0].name)

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

    def build_request(self, tag, target):
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
            "tag": {
                "@id": tag.urlid
            },
            "target": target,
        })