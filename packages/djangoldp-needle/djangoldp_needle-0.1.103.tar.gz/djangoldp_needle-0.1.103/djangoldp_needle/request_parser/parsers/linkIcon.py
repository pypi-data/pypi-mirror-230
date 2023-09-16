from . import AbstractParser
from ...models import AnnotationTarget
from urllib.parse import urlparse


class LinkIcon(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        if annotation_target.image is None:
            icon = bs_document.select("link[rel='icon']")
            image = None
            if icon is None:
                icon = bs_document.select("link[rel='shortcut icon']")
            if icon and icon[0].has_attr("href"):
                image = icon[0]["href"]

            if image is not None:
                annotation_target.image = image

        return True
