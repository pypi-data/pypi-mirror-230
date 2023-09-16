from . import AbstractParser
from .jsonld import JSONLD
from ...models import AnnotationTarget
import datetime


class MetaProp(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        selectors = ["meta[name='pubdate']", "meta[name='article:published_time']", "meta[name='DC:date']",
                     "meta[name='DC.date']", "meta[name='article:published_time']",
                     "meta[property='pubdate']", "meta[property='article:published_time']", "meta[property='DC:date']",
                     "meta[property='DC.date']", "meta[property='article:published_time']"]

        for selector in selectors:
            if annotation_target.publication_date is None:
                # print("selector", selector)
                date_published_element = bs_document.select(selector)
                if date_published_element:
                    content = date_published_element[0]["content"]
                    if content:
                        date = JSONLD().try_strptimeAll(content)
                        if date is not None:
                            annotation_target.publication_date = date.isoformat()

        if annotation_target.image is None:

            selectors = ["meta[name='og:image']","meta[property='og:image']","meta[name='twitter:image']","meta[property='twitter:image']"]

            for selector in selectors:
                if annotation_target.image is None:
                    image_element = bs_document.select(selector)
                    if image_element:
                        content = image_element[0]["content"]
                        annotation_target.image = content


        if annotation_target.image is None:

            selectors = ["meta[name='msapplication-TileImage']","meta[property='msapplication-TileImage']"]

            for selector in selectors:
                if annotation_target.image is None:
                    image_element = bs_document.select(selector)
                    if image_element:
                        content = image_element[0]["content"]
                        annotation_target.image = content

        return True
