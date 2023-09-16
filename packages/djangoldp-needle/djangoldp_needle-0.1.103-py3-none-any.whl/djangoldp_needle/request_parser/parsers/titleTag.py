from . import AbstractParser
from ...models import AnnotationTarget



class TitleTag(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        if annotation_target.title is None:
            title = bs_document.select("title")
            if title :
                content = title[0].contents
                if content:
                    annotation_target.title = content[0]


        return True
