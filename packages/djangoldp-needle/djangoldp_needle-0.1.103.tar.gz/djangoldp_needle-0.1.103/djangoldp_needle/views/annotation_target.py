from django.core.exceptions import ObjectDoesNotExist
from djangoldp.views import LDPViewSet, JSONLDParser, NoCSRFAuthentication
from rest_framework import status
import requests as requestsLib
import random as random
from urllib.parse import urlparse

from ..models import AnnotationTarget, NeedleActivity
from ..models.needle_activity import ACTIVITY_TYPE_FIRST_ANNOTATION_WITHOUT_CONNECTIONS
from rest_framework.views import APIView, Response

from ..request_parser import RequestParser
from requests.exceptions import ReadTimeout, ConnectionError, TooManyRedirects
from ..request_parser.webdriver_utils import get_webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import datetime


class AnnotationTargetViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        self.check_model_permissions(request)
        target = request.data['target']
        try:
            targets_in_db = AnnotationTarget.objects.get(target=target)
        except ObjectDoesNotExist:
            try:
                new_annotation = self.parse_target(target)

                # re check if target has a redirection
                try:
                    targets_in_db = AnnotationTarget.objects.get(target=new_annotation.target)
                except ObjectDoesNotExist:
                    return self.save_annotation_target(request, new_annotation)

            except Exception as e:
                return self.generate_invalide_response()

        return self.generate_success_response(status.HTTP_200_OK, targets_in_db)

    @staticmethod
    def parse_target(target_url):

        print("[TARGET] " + target_url)

        # Fix for http / https page and trailing / or not
        parsed_uri = urlparse(target_url)
        target_url_alt1 = target_url
        target_url_alt2 = target_url
        target_url_alt3 = target_url
        protocol = '{uri.scheme}'.format(uri=parsed_uri)

        if  protocol == 'http' :
            target_url_alt1 = 'https' + target_url[len(protocol):]
        elif protocol == 'https':
            target_url_alt1 = 'http' + target_url[len(protocol):]
        if target_url.endswith("/"):
            target_url_alt2 = target_url[:len(target_url)-1]
            target_url_alt3 = target_url_alt1[:len(target_url_alt1)-1]
        else:
            target_url_alt2 = target_url + '/'
            target_url_alt3 = target_url_alt1 + '/'

        annotation_target = None
        try:
            annotation_target = AnnotationTarget.objects.get(target=target_url)
        except ObjectDoesNotExist:
            try:
                annotation_target = AnnotationTarget.objects.get(target=target_url_alt1)
            except ObjectDoesNotExist:
                try:
                    annotation_target = AnnotationTarget.objects.get(target=target_url_alt2)
                except ObjectDoesNotExist:
                    try:
                        annotation_target = AnnotationTarget.objects.get(target=target_url_alt3)
                    except ObjectDoesNotExist:
                        print("[TARGET] NEW " + target_url)

        target_content = None
        target_content_type = None
        target_content_type_headers = None
        # retest if http only or no image
        if annotation_target is None or annotation_target.target.startswith('http://') or annotation_target.image is None:
            target_request_response = None

            try:
                target_content_type_headers = requestsLib.head(target_url, verify=False,
                                                               allow_redirects=True, timeout=20).headers
                if 'Content-Type' in target_content_type_headers:
                    target_content_type = target_content_type_headers['Content-Type']
                elif 'content-type' in target_content_type_headers:
                    target_content_type = target_content_type_headers['content-type']
            except TooManyRedirects:
                print("[TARGET] head " + target_url + " TooManyRedirects")
            except ReadTimeout:
                print("[TARGET] head " + target_url + " ReadTimeout")
            except ConnectionError:
                print("[TARGET] head " + target_url + " ConnectionError")

            try:
                target_request_response = requestsLib.get(target_url, verify=False,
                                                          allow_redirects=True, timeout=20,
                                                          cookies={
                                                              'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+{}'.format(
                                                                  random.randint(100, 999))})
                # target_content_type = target_request_response.headers['Content-Type']
                if target_content_type is None:
                    if target_content_type_headers is not None and 'Content-Type' in target_request_response.headers:
                        target_content_type = target_request_response.headers['Content-Type']
                    elif target_content_type_headers is not None and 'content-type' in target_content_type_headers:
                        target_content_type = target_request_response.headers['content-type']

                print("[TARGET] " + target_url + " " + str(target_request_response.status_code))
            except TooManyRedirects:
                print("[TARGET] " + target_url + " TooManyRedirects")
                target_request_response = None
            except ReadTimeout:
                print("[TARGET] " + target_url + " ReadTimeout")
                target_request_response = None
            except ConnectionError:
                print("[TARGET] " + target_url + " ConnectionError")
                target_request_response = None

            if target_request_response is not None and (
                    ("status_code" in target_request_response and target_request_response.status_code == 200) or (
                    target_request_response.status_code and target_request_response.status_code == 200)):
                target_content = target_request_response.content

            if target_content_type is None and target_url.lower().endswith(".pdf"):
                target_content_type = "application/pdf"

            if target_content_type is None and target_content is not None and "<html" in str(target_content).lower():
                target_content_type = "text/html"

            if target_content is None or target_content_type is None or "text/html" in target_content_type or "application/json" in target_content_type:
                if target_request_response is not None and target_request_response.text is not None:
                    target_content = target_request_response.text
                elif target_content is not None:
                    target_content = str(target_content)
                print("[TARGET] " + target_url + " with selenium")
                driver = None
                try:
                    # driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                    #                           options=chromeOptions)
                    driver = get_webdriver()
                    driver.get(target_url)
                    WebDriverWait(driver, 20).until(
                        expected_conditions.presence_of_element_located((By.TAG_NAME, "body")))
                    target_content = driver.page_source
                    if target_content_type is None and "<html" in target_content:
                        target_content_type = "text/html"
                except TimeoutException:
                    print("[TARGET] " + target_url + " selenium - TimeoutException")
                except WebDriverException:
                    print("[TARGET] " + target_url + " selenium - WebDriverException")
                except AttributeError:
                    print("[TARGET] " + target_url + " selenium - AttributeError - handle for tests")
                finally:
                    if driver is not None:
                        driver.close()
            elif target_request_response is not None:
                target_content = target_request_response.content

            if target_content is not None and len(str(target_content).strip()) > 0:
                print("[TARGET_CONTENT] not None")
                parser = RequestParser()
                (result, annotation_target_new) = parser.parse(target_url, target_content, target_content_type)
                target_url = annotation_target_new.target
                try:
                    annotation_target = AnnotationTarget.objects.get(target=target_url)
                except ObjectDoesNotExist:
                    print("[TARGET] NEW " + target_url)
                if annotation_target is None:
                    annotation_target = annotation_target_new
                    print("[TARGET] NEW " + annotation_target.target)
                else:
                    annotation_target.target = annotation_target_new.target
                    annotation_target.image = annotation_target_new.image
                    annotation_target.title = annotation_target_new.title
                    annotation_target.publication_date = annotation_target_new.publication_date
                    annotation_target.annotation_target_date = annotation_target_new.annotation_target_date
                    print("[TARGET] UPDATE " + annotation_target.target)
                # annotation_target.save()
            else:
                print("[TARGET_CONTENT] " + target_url + " invalid")
        return annotation_target

    def generate_success_response(self, status, target):
        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(target)
        headers = self.get_success_headers(data)
        return Response(data, status=status, headers=headers)

    def generate_invalide_response(self):
        return Response({'URL': ['Le lien est invalide']}, status=status.HTTP_400_BAD_REQUEST)

    def save_annotation_target(self, request, annotation_target):
        annotation_target.annotation_target_date = datetime.datetime.now()
        annotation_target.save()
        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(annotation_target)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        # Force empty list to avoid performance issues due to a large dataset

        serializer = self.get_serializer(AnnotationTarget.objects.none(), many=True)
        return Response(serializer.data)
