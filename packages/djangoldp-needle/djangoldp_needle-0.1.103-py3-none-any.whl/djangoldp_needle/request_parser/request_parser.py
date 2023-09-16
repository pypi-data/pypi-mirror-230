from .parsers import OpenGraph, JSONLD, ItemProp, MetaProp, LinkCanonicalProp, TitleTag, URLParser, LastChanceParser, \
    LinkIcon
from bs4 import BeautifulSoup
from ..models import AnnotationTarget
from urllib.parse import urlparse
import requests
from urllib.parse import urljoin
from requests.exceptions import ReadTimeout, ConnectionError, TooManyRedirects

class RequestParser:
    def __init__(self):
        self.parsers = [
            JSONLD(),
            MetaProp(),
            OpenGraph(),
            TitleTag(),
            LinkCanonicalProp(),
            ItemProp(),
            URLParser(),
            LinkIcon(),
            LastChanceParser()

        ]

    def parse(self, target_url, target_html, target_content_type):
        annotation_target = AnnotationTarget()
        response_head = None

        parse_valid = False
        if "text/html" in target_content_type or "application/json" in target_content_type \
                or "application/ld+json" in target_content_type or "text/plain" in target_content_type:
            beautiful_soup_document = BeautifulSoup(target_html, "html.parser")
            for parser in self.parsers:
                parser_parse_valid = parser.parse(annotation_target, target_url, beautiful_soup_document,
                                                  parse_valid)
                parse_valid = parse_valid or parser_parse_valid
        else:
            annotation_target.target = target_url
            parsed_url = urlparse(target_url)
            filename = parsed_url.path.split("/")[-1]
            annotation_target.title = filename
            response_head = None
            try :
                response_head = requests.head(target_url)
            except TooManyRedirects:
                print("[TARGET] head " + target_url + " TooManyRedirects")
            except ReadTimeout:
                print("[TARGET] head " + target_url + " ReadTimeout")
            except ConnectionError:
                print("[TARGET] head " + target_url + " ConnectionError")

            if response_head is not None:
                last_modified = None
                if "Last-Modified" in response_head.headers:
                    last_modified = response_head.headers.get("Last-Modified")
                elif "last-modified" in response_head.headers:
                    last_modified = response_head.headers.get("last-modified")

                if last_modified is not None:
                    jsonld_parser = JSONLD()
                    annotation_target.publication_date = jsonld_parser.try_strptimeAll(last_modified)

            if "application/pdf" in target_content_type:
                parse_valid = True
            else:
                if "image/jpeg" in target_content_type:
                    annotation_target.image = target_url
                    parse_valid = True
                elif "image/gif" in target_content_type:
                    annotation_target.image = target_url
                    parse_valid = True
                elif "image/png" in target_content_type:
                    annotation_target.image = target_url
                    parse_valid = True
                elif "image/svg" in target_content_type:
                    annotation_target.image = target_url
                    parse_valid = True
                else:
                    parse_valid = True

        if annotation_target and annotation_target.image and not annotation_target.image.startswith("http"):
            # parsed_uri = urlparse(annotation_target.target)
            # host_and_protocol = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            # protocol = '{uri.scheme}'.format(uri=parsed_uri)
            # host = '{uri.netloc}'.format(uri=parsed_uri)

            if annotation_target.image.startswith("/") or annotation_target.image.startswith(".") or not annotation_target.image.startswith("http"):
                annotation_target.image = urljoin(annotation_target.target,annotation_target.image)

        if response_head is None:
            try :
                response_head = requests.head(target_url)
            except TooManyRedirects:
                print("[TARGET] head " + target_url + " TooManyRedirects")
            except ReadTimeout:
                print("[TARGET] head " + target_url + " ReadTimeout")
            except ConnectionError:
                print("[TARGET] head " + target_url + " ConnectionError")

        if response_head is not None:
            content_location = None
            if "Content-Location" in response_head.headers:
                content_location = response_head.headers.get("Content-Location")
            elif "content-location" in response_head.headers:
                content_location = response_head.headers.get("content-location")

            if content_location is  None:
                if "Location" in response_head.headers:
                    content_location = response_head.headers.get("Location")
                elif "location" in response_head.headers:
                    content_location = response_head.headers.get("location")

            if content_location is not None:
                annotation_target.target = urljoin(annotation_target.target,content_location)

        if annotation_target and annotation_target.target and not annotation_target.target.startswith("http"):

            if annotation_target.target.startswith("/") or annotation_target.target.startswith(".") or not annotation_target.target.startswith("http"):
                annotation_target.target = urljoin(target_url,annotation_target.target)

        parsed_uri = urlparse(annotation_target.target)
        host_and_protocol = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        protocol = '{uri.scheme}'.format(uri=parsed_uri)
        host = '{uri.netloc}'.format(uri=parsed_uri)
        if annotation_target.target == host_and_protocol:
            annotation_target.target = host_and_protocol + "/"

        return parse_valid, annotation_target

