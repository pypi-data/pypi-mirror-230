import requests_mock
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json
import datetime
from pkg_resources import resource_string

from ..models import Booklet, BookletContributor, AnnotationTarget, Annotation

class TestBookletBulkDelete(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_bulk_delete_not_found(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.client.force_authenticate(user1)

        response = self.client.post(
            "/booklets/999/bulk_delete/",
            content_type='application/ld+json',
        )

        self.assertEqual(response.status_code, 404)

    def test_booklet_bulk_delete_bad_method(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet()
        contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        self.client.force_authenticate(user1)

        response = self.client.get(
            "/booklets/" + str(booklet.pk) + "/bulk_delete/",
            content_type='application/ld+json',
        )

        self.assertEqual(response.status_code, 405)

    def test_booklet_bulk_delete_not_contributor(self):
        user1 = self.buildUser('user1')
        booklet = self.store_booklet()
        self.client.force_authenticate(user1)

        response = self.client.post(
            "/booklets/" + str(booklet.pk) + "/bulk_delete/",
            content_type='application/ld+json',
        )

        self.assertEqual(response.status_code, 403)

    def test_booklet_bulk_delete_bad_permission(self):
        for role in (BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR):
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                booklet = self.store_booklet()
                contributor = self.store_booklet_contributor(booklet, user1, role)
                self.client.force_authenticate(user1)

                response = self.client.post(
                    "/booklets/" + str(booklet.pk) + "/bulk_delete/",
                    content_type='application/ld+json',
                )

                self.assertEqual(response.status_code, 403)

                transaction.savepoint_rollback(sid)

    def test_booklet_bulk_delete_success_filter_target(self):
        for role in (BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER):
            with transaction.atomic():
                sid = transaction.savepoint()

                target1 = AnnotationTarget(target='http://target1')
                target1.save()

                target2 = AnnotationTarget(target='http://target2')
                target2.save()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet = self.store_booklet()
                contributor1 = self.store_booklet_contributor(booklet, user1, role)
                contributor2 = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_VISIT)

                self.store_booklet_annotation_target(booklet, user1, target1)
                self.store_booklet_annotation_target(booklet, user2, target1)
                self.store_booklet_annotation_target(booklet, user2, target2)
                self.client.force_authenticate(user1)

                response = self.client.post(
                    "/booklets/" + str(booklet.pk) + "/bulk_delete/",
                    content_type='application/ld+json',
                    data=self._create_bulk_delete_request('http://target1')
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(3, Annotation.objects.count())

                annotations = booklet.annotations.all()
                self.assertEqual(1, len(annotations))
                self.assertEqual(target2, annotations[0].target)
                self.assertEqual(user2, annotations[0].creator)

                transaction.savepoint_rollback(sid)

    def test_booklet_bulk_delete_success_filter_booklet(self):
        for role in (BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER):
            with transaction.atomic():
                sid = transaction.savepoint()

                target1 = AnnotationTarget(target='http://target1')
                target1.save()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')
                booklet1 = self.store_booklet()
                booklet2 = self.store_booklet()
                contributor1 = self.store_booklet_contributor(booklet1, user1, role)
                contributor2 = self.store_booklet_contributor(booklet2, user2, BookletContributor.ROLE_VISIT)

                self.store_booklet_annotation_target(booklet1, user1, target1)
                self.store_booklet_annotation_target(booklet2, user2, target1)
                self.client.force_authenticate(user1)

                response = self.client.post(
                    "/booklets/" + str(booklet1.pk) + "/bulk_delete/",
                    content_type='application/ld+json',
                    data=self._create_bulk_delete_request('http://target1')
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(2, Annotation.objects.count())

                self.assertEqual(0, len(booklet1.annotations.all()))
                annotations = booklet2.annotations.all()
                self.assertEqual(1, len(annotations))
                self.assertEqual(target1, annotations[0].target)
                self.assertEqual(user2, annotations[0].creator)

                transaction.savepoint_rollback(sid)

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

    def store_booklet_annotation_target(self, booklet, user, target):
        annotation = Annotation(target=target, creator=user)
        annotation.save()

        booklet.annotations.add(annotation)

    def _create_bulk_delete_request(self, target):
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
            "target": target
        })