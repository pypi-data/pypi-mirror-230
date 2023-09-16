from . import AbstractParser
from ...models import AnnotationTarget
# from rdflib import Graph
import json
import datetime
import re
from urllib.parse import urlparse


class JSONLD(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        accepted_types = [
            "Article",
            "AdvertiserContentArticle",
            "NewsArticle",
            "AnalysisNewsArticle",
            "AskPublicNewsArticle",
            "BackgroundNewsArticle",
            "OpinionNewsArticle",
            "ReportageNewsArticle",
            "ReviewNewsArticle",
            "Report",
            "SatiricalArticle",
            "ScholarlyArticle",
            "MedicalScholarlyArticle",
            "SocialMediaPosting",
            "BlogPosting",
            "LiveBlogPosting",
            "DiscussionForumPosting",
            "TechArticle",
            "APIReference",
            "Review",
            "ClaimReview",
            "CriticReview",
            "ReviewNewsArticle",
            "EmployerReview",
            "MediaReview",
            "Recommendation",
            "UserReview",
            "WebContent",
            "HealthTopicContent",
            "Event",
            "BusinessEvent",
            "ChildrensEvent",
            "ComedyEvent",
            "CourseInstance",
            "DanceEvent",
            "DeliveryEvent",
            "EducationEvent",
            "EventSeries",
            "ExhibitionEvent",
            "Festival",
            "FoodEvent"]

        jsonElements = bs_document.find_all("script", {"type": "application/ld+json"})
        for jsonElement in jsonElements:
            if (jsonElement):
                values = None
                try:
                    values = json.loads("".join(jsonElement.contents))
                except json.decoder.JSONDecodeError:
                    print("error in JSON decoding")
                if values is not None:
                    if not isinstance(values, list):
                        values = [values]
                    for value in values:
                        # and (value.get("@type") == "NewsArticle"
                        #      or value.get("@type") == "NewsArticle"
                        if value and value.get("@type"):
                            type = value.get("@type")
                            if type and type in accepted_types:
                                jsonld_string = json.dumps(value)
                                if jsonld_string:
                                    # result = Graph().parse(data=jsonld_string, format='json-ld')
                                    datePublished = value.get("datePublished")
                                    date = None
                                    if datePublished:
                                        date = self.try_strptimeAll(str(datePublished))
                                        if date is not None:
                                            annotation_target.publication_date = date.isoformat()
                                    if date is None:
                                        dateCreated = value.get("dateCreated")
                                        if dateCreated:
                                            date = self.try_strptimeAll(str(dateCreated))
                                            if date is not None:
                                                annotation_target.publication_date = date.isoformat()
                                    image = value.get("image")
                                    if image:
                                        if isinstance(image, dict):
                                            image_url = image.get("url")
                                            if (image_url):
                                                annotation_target.image = image_url
                                        else:
                                            if isinstance(image, list):
                                                image = image[0]
                                                if isinstance(image, dict):
                                                    image_url = image.get("url")
                                                    if isinstance(image_url, list):
                                                        image_url = image_url[0]
                                                    if image_url:
                                                        annotation_target.image = image_url
                                                    else:
                                                        image_url = image.get("contentUrl")
                                                        if isinstance(image_url, list):
                                                            image_url = image_url[0]
                                                        if image_url:
                                                            annotation_target.image = image_url
                                                else:
                                                    annotation_target.image = str(image)
                                            else:
                                                annotation_target.image = str(image)

                                    headline = value.get("headline")

                                    if (headline):
                                        annotation_target.title = headline
                                    else:
                                        name = value.get("name")
                                        if (name):
                                            annotation_target.title = name
        return True

    def try_strptime(self, s, format):
        try:
            date = datetime.datetime.strptime(s, format)
        except ValueError:
            date = None
        return date

    def try_strptimeAll(self, dateString):
        # print("try_strptimeAll", dateString)
        if dateString.find(',') >= 0:
            dateString = dateString[dateString.find(',') + 1:]
        dateStringSave = dateString
        dateString = dateString.replace("UTC", "").strip()
        dateString = dateString.replace("GMT", "").strip()
        p = re.compile(
            "^20[0-9][0-9].*", re.DOTALL)
        startsWithYear = p.match(dateString)
        cutIndex = dateString.find("+")
        if cutIndex < 0 and dateString.find("-") > len(dateString) - 5:
            cutIndex = dateString.find("-")
        if cutIndex < 0 and dateString.endswith("00:00"):
            cutIndex = len(dateString) - 5
        if cutIndex < 0:
            cutIndex = dateString.find(".")
        if cutIndex < 0 and dateString.endswith("0000"):
            cutIndex = len(dateString) - 4
        if startsWithYear:
            date = self.try_strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')
            if date is None:
                date = self.try_strptime(dateString, '%Y/%m/%dT%H:%M:%S%z')
                if date is None:
                    date = self.try_strptime(dateString, '%Y-%m-%dT%H:%M:%S %z')
                    if date is None:
                        date = self.try_strptime(dateString, '%Y/%m/%dT%H:%M:%S %z')
                        if date is None:
                            date = self.try_strptime(dateString, '%Y-%m-%dT%H:%M:%SZ')
                            if date is None:
                                date = self.try_strptime(dateString, '%Y/%m/%dT%H:%M:%SZ')
                                if date is None:
                                    date = self.try_strptime(dateString, '%Y-%m-%dT%H:%M:%S.%f')
                                    if date is None:
                                        date = self.try_strptime(dateString, '%Y/%m/%dT%H:%M:%S.%f')
                                        if date is None:
                                            date = self.try_strptime(dateString, '%Y-%m-%d %H:%M:%S.%f')
                                            if date is None:
                                                date = self.try_strptime(dateString, '%Y/%m/%d %H:%M:%S.%f')

                                                if date is None:
                                                    date = self.try_strptime(dateString, '%Y-%m-%dT%H:%M:%S')
                                                    if date is None:
                                                        date = self.try_strptime(dateString, '%Y/%m/%dT%H:%M:%S')
                                                        if date is None:
                                                            date = self.try_strptime(dateString, '%Y-%m-%d %H:%M:%S')
                                                            if date is None:
                                                                date = self.try_strptime(dateString,
                                                                                         '%Y/%m/%d %H:%M:%S')
                                                                if date is None:
                                                                    date = self.try_strptime(dateString,
                                                                                             '%Y/%m/%d - %H:%M')
                                                                    if date is None:
                                                                        date = self.try_strptime(dateString, '%Y-%m-%d')
                                                                        if date is None:
                                                                            date = self.try_strptime(dateString,
                                                                                                     '%Y/%m/%d')
                                                                            if date is None:
                                                                                date = self.try_strptime(dateString,
                                                                                                         '%Y%m%d')
                                                                                if date is None and cutIndex < 0:
                                                                                    p = re.compile(
                                                                                        ".*((20[0-9][0-9])[\/|-]([0-1]{0,1}[0-9])[\/|-]([0-2]{0,1}[0-9])).*")
                                                                                    result = p.search(dateString)
                                                                                    if result:
                                                                                        dateString = result.group(1)
                                                                                        date = self.try_strptime(
                                                                                            dateString, '%Y/%m/%d')
                                                                                        if date is None:
                                                                                            date = self.try_strptime(
                                                                                                dateString,
                                                                                                '%Y-%m-%d')
                                                                                    else:
                                                                                        p = re.compile(
                                                                                            ".*((20[0-9][0-9])[\/|-]([0-1]{0,1}[0-9]))")
                                                                                        result = p.search(dateString)
                                                                                        if result:
                                                                                            dateString = result.group(1)
                                                                                            if date is None:
                                                                                                date = self.try_strptime(
                                                                                                    dateString,
                                                                                                    '%Y/%m')
                                                                                                if date is None:
                                                                                                    date = self.try_strptime(
                                                                                                        dateString,
                                                                                                        '%Y-%m')
                                                                                        else:
                                                                                            p = re.compile(
                                                                                                ".*(20[0-9][0-9])")
                                                                                            result = p.search(
                                                                                                dateString)
                                                                                            if result:
                                                                                                dateString = result.group(
                                                                                                    1)
                                                                                                date = self.try_strptime(
                                                                                                    dateString,
                                                                                                    '%Y')
        else:
            date = self.try_strptime(dateString, '%d-%m-%YT%H:%M:%S.%f')
            if date is None:
                date = self.try_strptime(dateString, '%d/%m/%YT%H:%M:%S.%f')
                if date is None:
                    date = self.try_strptime(dateString, '%m-%d-%YT%H:%M:%S.%f')
                    if date is None:
                        date = self.try_strptime(dateString, '%m/%d/%YT%H:%M:%S.%f')
                        if date is None:
                            date = self.try_strptime(dateString, '%d-%m-%Y %H:%M:%S.%f')
                            if date is None:
                                date = self.try_strptime(dateString, '%d/%m/%Y %H:%M:%S.%f')
                                if date is None:
                                    date = self.try_strptime(dateString, '%m-%d-%Y %H:%M:%S.%f')
                                    if date is None:
                                        date = self.try_strptime(dateString, '%m/%d/%Y %H:%M:%S.%f')
                                        if date is None:
                                            date = self.try_strptime(dateString, '%d-%m-%YT%H:%M:%S')
                                            if date is None:
                                                date = self.try_strptime(dateString, '%d/%m/%YT%H:%M:%S')
                                                if date is None:
                                                    date = self.try_strptime(dateString, '%d-%m-%Y %H:%M:%S')
                                                    if date is None:
                                                        date = self.try_strptime(dateString, '%d/%m/%Y %H:%M:%S')
                                                        if date is None:
                                                            date = self.try_strptime(dateString, '%m-%d-%Y %H:%M:%S')
                                                            if date is None:
                                                                date = self.try_strptime(dateString,
                                                                                         '%m/%d/%Y %H:%M:%S')
                                                                if date is None:
                                                                    date = self.try_strptime(
                                                                        dateString,
                                                                        '%d %b %Y  %H:%M:%S')
                                                                    if date is None:
                                                                        date = self.try_strptime(
                                                                            dateString,
                                                                            '%d %b. %Y  %H:%M:%S')
                                                                        if date is None:
                                                                            date = self.try_strptime(
                                                                                dateString,
                                                                                '%d %B %Y  %H:%M:%S')
                                                                            if date is None:
                                                                                date = self.try_strptime(dateString,
                                                                                                         '%d/%m/%Y %H:%M')
                                                                                if date is None:
                                                                                    date = self.try_strptime(dateString,
                                                                                                             '%m/%d/%Y %H:%M')

                                                                                    if date is None:
                                                                                        date = self.try_strptime(
                                                                                            dateString,
                                                                                            '%d/%m/%Y - %H:%M')
                                                                                        if date is None:
                                                                                            date = self.try_strptime(
                                                                                                dateString,
                                                                                                '%m/%d/%Y - %H:%M')
                                                                                            if date is None:
                                                                                                date = self.try_strptime(
                                                                                                    dateString,
                                                                                                    '%d-%m-%Y')
                                                                                                if date is None:
                                                                                                    date = self.try_strptime(
                                                                                                        dateString,
                                                                                                        '%m-%d-%Y')
                                                                                                    if date is None:
                                                                                                        date = self.try_strptime(
                                                                                                            dateString,
                                                                                                            '%d/%m/%Y')
                                                                                                        if date is None:
                                                                                                            date = self.try_strptime(
                                                                                                                dateString,
                                                                                                                '%m/%d/%Y')
                                                                                                            if date is None:
                                                                                                                date = self.try_strptime(
                                                                                                                    dateString,
                                                                                                                    '%d %b %Y')
                                                                                                                if date is None:
                                                                                                                    date = self.try_strptime(
                                                                                                                        dateString,
                                                                                                                        '%d %b. %Y')
                                                                                                                    if date is None:
                                                                                                                        date = self.try_strptime(
                                                                                                                            dateString,
                                                                                                                            '%d %B %Y')
                                                                                                                        if date is None:
                                                                                                                            p = re.compile(
                                                                                                                                "^[0-9]+$",
                                                                                                                                re.DOTALL)
                                                                                                                            timestamp = p.match(
                                                                                                                                dateString)
                                                                                                                            if timestamp and len(
                                                                                                                                    dateString) == 13:
                                                                                                                                date = datetime.datetime.fromtimestamp(
                                                                                                                                    int(dateString) / 1000)
                                                                                                                            elif timestamp and len(
                                                                                                                                    dateString) == 10:
                                                                                                                                date = datetime.datetime.fromtimestamp(
                                                                                                                                    int(dateString))
        # if date is not None:
        # print("try_strptimeAll", date.isoformat())
        if date is None:

            if cutIndex > 0:
                dateCut = dateStringSave[:cutIndex].strip()
                date = self.try_strptimeAll(dateCut)
        # if date is None:
        #     print("failed date " + dateString)
        return date
