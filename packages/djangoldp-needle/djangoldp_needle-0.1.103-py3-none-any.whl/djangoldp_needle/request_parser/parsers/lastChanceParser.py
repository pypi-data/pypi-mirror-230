from . import AbstractParser
from ...models import AnnotationTarget
import datetime


class LastChanceParser(AbstractParser):

    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        if annotation_target.publication_date is None:
            annotation_target.publication_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')
        if annotation_target.target is None or len(annotation_target.target.strip()) == 0:
            annotation_target.target = target_url
        if annotation_target.title is None or len(annotation_target.title.strip()) == 0:
            annotation_target.title = target_url
        # if annotation_target.image is None:
        #     annotation_target.image =  lien vers une image statique
        return True
