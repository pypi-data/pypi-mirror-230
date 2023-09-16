import requests_mock
from django.db import transaction
from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase
import json
import datetime
from pkg_resources import resource_string

from ..models import AnnotationTarget

from .data.target_url.realsites import real_sites

from .data.target_url.needlerealsites import needle_real_sites
from django.conf import settings
import re


@requests_mock.Mocker(real_http=True)
class TestAnnotationTargetAdd(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()
        return user

    # def test_annotation_parse_real_site(self, m):
    #     user1 = self.buildUser('user1')
    #     self.client.force_authenticate(user1)
    #
    #     for site_extract, expected_target, expected_title, expected_img, expected_publication, expected_canonical_target in real_sites:
    #         with transaction.atomic():
    #             # Creates a new savepoint. Returns the savepoint ID (sid).
    #             sid = transaction.savepoint()
    #
    #             self._mock_response_content_from_file(m, site_extract)
    #             response = self.client.post(
    #                 "/annotationtargets/",
    #                 content_type='application/ld+json',
    #                 data=self._create_annotation_parse_request()
    #             )
    #             self.assertEqual(response.status_code, 201)
    #
    #             print(expected_target)
    #
    #             response_decoded = json.loads(response.content)
    #             self.assertEqual(response_decoded['@id'], 'http://happy-dev.fr/annotationtargets/1/')
    #             self.assertEqual(response_decoded['target'], expected_canonical_target)
    #             self.assertEqual(response_decoded['title'], expected_title)
    #             self.assertEqual(response_decoded['image'], expected_img)
    #             if expected_publication is None:
    #                 expected_publication = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')
    #                 self.assertEqual(response_decoded['publication_date'][:10], expected_publication[:10])
    #
    #             else:
    #                 # try:
    #                     self.assertEqual(response_decoded['publication_date'],
    #                                      expected_publication[:len(response_decoded['publication_date'])])
    #                     #
    #                     # if response_decoded['publication_date'] == expected_publication or datetime.datetime.fromisoformat(
    #                     #         response_decoded['publication_date']) == datetime.datetime.fromisoformat(
    #                     #         expected_publication):
    #                     #     self.assertTrue(response_decoded[
    #                     #                         'publication_date'] == expected_publication or datetime.datetime.fromisoformat(
    #                     #         response_decoded['publication_date']) == datetime.datetime.fromisoformat(
    #                     #         expected_publication))
    #                 # except ValueError:
    #                 #     self.assertEqual(response_decoded['publication_date'], expected_publication)
    #             # Rolls back the transaction to savepoint sid.
    #             transaction.savepoint_rollback(sid)

    def test_annotation_multiple_request_same_target(self, m):
        user1 = self.buildUser('user1')
        self.client.force_authenticate(user1)

        self.assertEqual(0, AnnotationTarget.objects.count())

        self._mock_response_content_from_file(m, 'data/parsing/base_valid.20221103.html')
        response = self.client.post(
            "/annotationtargets/",
            content_type='application/ld+json',
            data=self._create_annotation_parse_request()
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(1, AnnotationTarget.objects.count())

        response = self.client.post(
            "/annotationtargets/",
            content_type='application/ld+json',
            data=self._create_annotation_parse_request()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AnnotationTarget.objects.count())

    def _test_annotation_invalid(self, m):
        user1 = self.buildUser('user1')
        self.client.force_authenticate(user1)

        self._mock_response_content_from_file(m, 'data/parsing/base_invalid.20221103.html')
        response = self.client.post(
            "/annotationtargets/",
            content_type='application/ld+json',
            data=self._create_annotation_parse_request()
        )
        self.assertEqual(response.status_code, 400)
        response_decoded = json.loads(response.content)
        self.assertEqual(response_decoded['URL'], ['Le lien est invalide'])
        self.assertEqual(0, AnnotationTarget.objects.count())

    def test_annotation_404(self, m):
        user1 = self.buildUser('user1')
        self.client.force_authenticate(user1)

        m.register_uri(
            'GET',
            'http://test.startinblox.com',
            text='',
            status_code=404
        )
        response = self.client.post(
            "/annotationtargets/",
            content_type='application/ld+json',
            data=self._create_annotation_parse_request()
        )
        self.assertEqual(response.status_code, 400)
        response_decoded = json.loads(response.content)
        self.assertEqual(response_decoded['URL'], ['Le lien est invalide'])
        self.assertEqual(0, AnnotationTarget.objects.count())

    def _create_annotation_parse_request(self):
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
            "target": "http://test.startinblox.com"
        })

    def _mock_response_content_from_file(self, m, file):
        file_content = resource_string(__name__, file).decode("utf-8")
        m.register_uri(
            'GET',
            'http://test.startinblox.com',
            text=file_content,
        )

    def _mock_response_content_from_file_and_url(self, m, file, url):
        file_content = resource_string(__name__, file).decode("utf-8")
        m.register_uri(
            'GET',
            url,
            text=file_content,
        )

    # def test_annotation_parse_request_from_needle_urls(self, m):
    #     user1 = self.buildUser('user1')
    #     self.client.force_authenticate(user1)
    #     counter = 0
    #     for site_extract, url, title, image, date, canonical_url in needle_real_sites:
    #         print("url            :" + url)
    #         self._mock_response_content_from_file_and_url(m, site_extract, url)
    #
    #         data = self._create_annotation_parse_request_from_url(url)
    #         response = self.client.post(
    #             "/annotationtargets/",
    #             content_type='application/ld+json',
    #             data=data
    #         )
    #
    #         self.assertEqual(response.status_code, 201)
    #
    #         response_decoded = response.json()
    #
    #         target_response = response_decoded['target']
    #         if target_response.find("http://") == 0:
    #             target_response = target_response[7:]
    #         elif target_response.find("https://") == 0:
    #             target_response = target_response[8:]
    #         #
    #         target_request = canonical_url
    #         if target_request.find("http://") == 0:
    #             target_request = target_request[7:]
    #         elif target_request.find("https://") == 0:
    #             target_request = target_request[8:]
    #         # if target_request.find("#") > 0:
    #         #     target_request = target_request[:target_request.find("#")]
    #         # if target_request.find("?") > 0:
    #         #     target_request = target_request[:target_request.find("?")]
    #         #
    #         # if target_request.find("www.") == 0 and target_response.find("www.") < 0:
    #         #     target_request = target_request[4:]
    #         # if target_response.find("www.") == 0 and target_request.find("www.") < 0:
    #         #     target_response = target_response[4:]
    #         # target_request = target_request.replace('//', '/')
    #         # target_response = target_response.replace('//', '/')
    #         # print("target_request :" + target_request)
    #         # print("target_response:" + target_response)
    #         # print("target_check   :" + ("OK" if target_response == target_request else "FAILED"))
    #         expected_id = settings.BASE_URL + '/annotationtargets/' + str(counter) + '/'
    #         print("expected_id :" + expected_id)
    #         print("id          :" + response_decoded['@id'])
    #         print("td_check    :" + ("OK" if expected_id == response_decoded['@id'] else "FAILED"))
    #         if counter == 0:
    #             url = response_decoded['@id']
    #             m = re.search(r'/\d+/', url)
    #             counter_str = m.group()
    #             counter_str = counter_str[1:-1]
    #             counter = int(counter_str)
    #         else:
    #             self.assertEqual(response_decoded['@id'], expected_id)
    #         self.assertEqual(target_response, target_request)
    #         self.assertEqual(response_decoded['title'], title)
    #         if image:
    #             self.assertEqual(response_decoded['image'], image)
    #         if date:
    #             date_to_compare_to = response_decoded['publication_date']
    #             if date_to_compare_to.endswith('Z'):
    #                 date_to_compare_to = date_to_compare_to[:len(date_to_compare_to) - 1]
    #             self.assertEqual(date_to_compare_to, date[:len(date_to_compare_to)])
    #
    #         counter = counter + 1

    def _create_annotation_parse_request_from_url(self, url):
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
            "target": url
        })

    # def test_request_redirect(self, m):
    #     response = requests.get("https://www.inaglobal.fr/numerique/article/l-internet-libre-et-gratuit-c-est-bien-fini-9725",verify=False)
    #     if response.history:
    #         print("Request was redirected")
    #         for resp in response.history:
    #             print(resp.status_code, resp.url)
    #         print("Final destination:")
    #         print(response.status_code, response.url)
    #     else:
    #         print("Request was not redirected")
    #
    # def test_request_header(self, m):
    #     response = requests.get("http://www.xhaus.com/headers")
    #     print(response.content)

    # def test_annotation_parse_request_from_needle_urls_with_redirect(self, m):
    #     user1 = self.buildUser('user1')
    #     self.client.force_authenticate(user1)
    #     counter = 0
    #     for link in linksWithRedirect:
    #         url = link.get('url')
    #         print("url            :" + url)
    #         title = link.get('title')
    #         date = link.get('date')
    #         image = link.get('image')
    #
    #         data = self._create_annotation_parse_request_from_url(url)
    #         # Creates a new savepoint. Returns the savepoint ID (sid).
    #         response = self.client.post(
    #             "/annotationtargets/",
    #             content_type='application/ld+json',
    #             data=data
    #         )
    #         self.assertEqual(response.status_code, 201)
    #
    #         response_decoded = response.json()
    #
    #         target_response = response_decoded['target']
    #         if target_response.find("http://") == 0:
    #             target_response = target_response[7:]
    #         elif target_response.find("https://") == 0:
    #             target_response = target_response[8:]
    #
    #         redirect_expected = linksWithRedirectExpected[counter].get('url')
    #         if redirect_expected.find("http://") == 0:
    #             redirect_expected = redirect_expected[7:]
    #         elif redirect_expected.find("https://") == 0:
    #             redirect_expected = redirect_expected[8:]
    #         if redirect_expected.find("#") > 0:
    #             redirect_expected = redirect_expected[:redirect_expected.find("#")]
    #
    #         if redirect_expected.find("www.") == 0 and target_response.find("www.") < 0:
    #             redirect_expected = redirect_expected[4:]
    #         if target_response.find("www.") == 0 and redirect_expected.find("www.") < 0:
    #             target_response = target_response[4:]
    #         redirect_expected = redirect_expected.replace('//', '/')
    #         target_response = target_response.replace('//', '/')
    #         print("redirect_expected :" + redirect_expected)
    #         print("target_response   :" + target_response)
    #         print("target_check      :" + ("OK" if target_response == redirect_expected else "FAILED"))
    #         expected_id = 'http://happy-dev.fr/annotationtargets/' + str(counter + 1) + '/'
    #         print("expected_id :" + expected_id)
    #         print("id          :" + response_decoded['@id'])
    #         print("td_check    :" + ("OK" if expected_id == response_decoded['@id'] else "FAILED"))
    #         self.assertEqual(response_decoded['@id'], expected_id)
    #         self.assertEqual(target_response, redirect_expected)
    #         # self.assertEqual(response_decoded['title'], title)
    #         # if image:
    #         #     self.assertEqual(response_decoded['image'], image)
    #         # else:
    #         #     self.assertTrue(response_decoded['image'])
    #         # if date:
    #         #     self.assertEqual(response_decoded['publication_date'], date)
    #         # else:
    #         #     self.assertTrue(response_decoded['publication_date'])
    #
    #         counter = counter + 1
    #
    #
    # def test_annotation_parse_request_from_needle_urls_not_found(self, m):
    #     user1 = self.buildUser('user1')
    #     self.client.force_authenticate(user1)
    #     for link in linksWithNotFound:
    #         url = link.get('url')
    #         print("url            :" + url)
    #
    #         data = self._create_annotation_parse_request_from_url(url)
    #         # Creates a new savepoint. Returns the savepoint ID (sid).
    #         response = self.client.post(
    #             "/annotationtargets/",
    #             content_type='application/ld+json',
    #             data=data
    #         )
    #         self.assertGreaterEqual(response.status_code, 400)
    #         self.assertLess(response.status_code, 500)
