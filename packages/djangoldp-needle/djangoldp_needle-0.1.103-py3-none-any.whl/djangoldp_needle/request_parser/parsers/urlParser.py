from . import AbstractParser
from ...models import AnnotationTarget
import re
import datetime

class URLParser(AbstractParser):


    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):



        if annotation_target.publication_date is None:

            if annotation_target.target is not None:
                date = self.parsedatefromurl(annotation_target.target)

            if date is None:
                date = self.parsedatefromurl(target_url)

            if date:
                annotation_target.publication_date = date.isoformat()

        return True

    def parsedatefromurl(self, urlString):
        if urlString:
            p = re.compile("http(s){0,1}:\/\/.*\/((20[0-9][0-9])\/([0-1]{0,1}[0-9])\/([0-2]{0,1}[0-9]))\/.*")
            result = p.search(urlString)
            if result:
                date = result.group(2)
                date = datetime.datetime.strptime(date, "%Y/%m/%d")
                return date
        return None