from . import AbstractParser
from . import JSONLD
from ...models import AnnotationTarget
from urllib.parse import urlparse


class OpenGraph(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result

        # if og_url is None:
        #     return False

        # if og_image is None:
        #     return False

        # if og_title is None:
        #     return False
        if(bs_document.head) :
            if annotation_target.publication_date is None:
                og_published = bs_document.head.find('meta', property="og:article:published_time")
                if og_published is not None and 'content' in og_published:
                    date = JSONLD().try_strptimeAll(og_published['content'])
                    if date is not None:
                        annotation_target.publication_date = date.isoformat()
                else:
                    og_published = bs_document.head.find('meta', property="og:updated_time")
                    if og_published is not None and 'content' in og_published:
                        date = JSONLD().try_strptimeAll(og_published['content'])
                        if date is not None :
                            annotation_target.publication_date = date.isoformat()

            if annotation_target.target is None or len(annotation_target.target.strip()) == 0:
                og_url = bs_document.head.find('meta', property="og:url")
                if og_url:
                    annotation_target.target = og_url['content']

            if annotation_target.image is None or len(annotation_target.image.strip()) == 0:
                og_image = bs_document.head.find('meta', property="og:image")
                if og_image:
                    if 'content' in og_image:
                        annotation_target.image = og_image['content'];

            if annotation_target.title is None or len(annotation_target.title.strip()) == 0:
                og_title = bs_document.head.find('meta', property="og:title")
                if og_title:
                    annotation_target.title = og_title['content']

        return True
