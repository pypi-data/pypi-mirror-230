from . import AbstractParser
from ...models import AnnotationTarget



class LinkCanonicalProp(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        if annotation_target.target is None :
            link = bs_document.select("link[rel='canonical']")
            if link :
                content = link[0]["href"]
                if content:
                    annotation_target.target = content


        return True
