import json

from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from ..models import Booklet, BookletContributor, Annotation

class TestBookletAddAnnotation(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    def test_booklet_add_annotation_booklet_public_annotation_open_as_non_contributor(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        booklet = self.store_booklet(public=True, collaboration=True)
        self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        annotation = self.store_annotation(user2)

        self.client.force_authenticate(user2)
        response = self.client.patch(
            "/booklets/" + str(booklet.pk) + "/",
            content_type='application/ld+json',
            data=self._create_request([annotation])
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, booklet.annotations.count())

        contributors = BookletContributor.objects.all()
        self.assertEqual(2, len(contributors))
        self.assertEqual(user2, contributors[1].user)
        self.assertEqual(booklet, contributors[1].booklet)
        self.assertEqual(BookletContributor.ROLE_VISIT, contributors[1].role)

    def test_booklet_add_annotation_role_owner(self):
        user1 = self.buildUser('user1')

        booklet = self.store_booklet()
        booklet_contributor = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_OWNER)
        annotation = self.store_annotation(user1)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/booklets/" + str(booklet.pk) + "/",
            content_type='application/ld+json',
            data=self._create_request([annotation])
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, booklet.annotations.count())

    def test_booklet_add_annotation_collaboration_open(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')

                booklet = self.store_booklet(collaboration=True)
                booklet_contributor = self.store_booklet_contributor(booklet, user1, role[0])
                annotation = self.store_annotation(user1)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([annotation])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(1, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_remove_annotation_collaboration_open_no_annotation_creator_not_moderator(self):
        for role in [BookletContributor.ROLE_VISIT, BookletContributor.ROLE_CONTRIBUTOR]:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')

                booklet = self.store_booklet(collaboration=True)
                booklet_contributor1 = self.store_booklet_contributor(booklet, user2, BookletContributor.ROLE_OWNER)
                booklet_contributor2 = self.store_booklet_contributor(booklet, user1, role[0])
                annotation = self.store_annotation(user2)

                booklet.annotations.add(annotation)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 400)
                self.assertTrue('Cannot remove annotation not creator' in response_value['non_field_errors'])
                self.assertEqual(1, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_remove_annotation_collaboration_open_no_annotation_creator_not_moderator(self):
        for role in [BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')

                booklet = self.store_booklet(collaboration=True)
                booklet_contributor1 = self.store_booklet_contributor(booklet, user2,
                                                                      BookletContributor.ROLE_OWNER)
                booklet_contributor2 = self.store_booklet_contributor(booklet, user1, role[0])
                annotation = self.store_annotation(user2)

                booklet.annotations.add(annotation)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(0, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_remove_annotation_collaboration_open_annotation_creator(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')

                booklet = self.store_booklet(collaboration=True)
                booklet_contributor = self.store_booklet_contributor(booklet, user1, role[0])
                annotation = self.store_annotation(user1)

                booklet.annotations.add(annotation)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(0, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_remove_annotation_collaboration_open_annotation_creator_mixed(self):
        for role in BookletContributor.ROLE_CHOICES:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')
                user2 = self.buildUser('user2')

                booklet = self.store_booklet(collaboration=True)
                booklet_contributor2 = self.store_booklet_contributor(booklet, user2,
                                                                      BookletContributor.ROLE_OWNER)
                booklet_contributor1 = self.store_booklet_contributor(booklet, user1, role[0])
                annotation2 = self.store_annotation(user2)
                annotation1 = self.store_annotation(user1)

                booklet.annotations.add(annotation1)
                booklet.annotations.add(annotation2)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([annotation2])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(1, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def test_booklet_add_annotation_collaboration_closed_role_VISIT(self):
        user1 = self.buildUser('user1')

        booklet = self.store_booklet(collaboration=False)
        booklet_contributor1 = self.store_booklet_contributor(booklet, user1, BookletContributor.ROLE_VISIT)
        annotation1 = self.store_annotation(user1)

        self.client.force_authenticate(user1)
        response = self.client.patch(
            "/booklets/" + str(booklet.pk) + "/",
            content_type='application/ld+json',
            data=self._create_request([annotation1])
        )
        response_value = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue('Cannot add annotation to not collaboration booklet when contributor' in response_value['non_field_errors'])
        self.assertEqual(0, booklet.annotations.count())

    def test_booklet_add_annotation_collaboration_closed_role_non_VISIT(self):
        for role in [BookletContributor.ROLE_CONTRIBUTOR, BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
            with transaction.atomic():
                sid = transaction.savepoint()

                user1 = self.buildUser('user1')

                booklet = self.store_booklet(collaboration=False)
                booklet_contributor1 = self.store_booklet_contributor(booklet, user1, role)
                annotation1 = self.store_annotation(user1)

                self.client.force_authenticate(user1)
                response = self.client.patch(
                    "/booklets/" + str(booklet.pk) + "/",
                    content_type='application/ld+json',
                    data=self._create_request([annotation1])
                )
                response_value = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(1, booklet.annotations.count())

                transaction.savepoint_rollback(sid)

    def _create_request(self, annotations):
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
            "annotations": {
                "ldp:contains": list(map(lambda annotation: {'@id': annotation.urlid}, annotations))
            }
        })

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

    def store_annotation(self, user):
        annotation = Annotation(
            creator=user,
        )
        annotation.save()

        return annotation
