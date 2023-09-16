from . import AbstractParser
from ...models import AnnotationTarget
from .jsonld import JSONLD


class ItemProp(AbstractParser):
    def parse(self, annotation_target: AnnotationTarget, target_url, bs_document, previous_parse_result):
        # Does not change result if previous parse match
        # if previous_parse_result:
        #     return previous_parse_result
        if annotation_target.publication_date is None:
            date_published_element = bs_document.select("[itemProp='datePublished']")
            if date_published_element:
                content = None
                if  date_published_element[0].has_attr("content"):
                    content = date_published_element[0]["content"]
                elif date_published_element[0].has_attr("datetime"):
                    content = date_published_element[0]["datetime"]
                else:
                    content = date_published_element[0].string
                if content is not None:
                    date = JSONLD().try_strptimeAll(content)
                    if date is not None:
                        annotation_target.publication_date = date.isoformat()

        if annotation_target.image is None:
            image_element = bs_document.select("[itemProp='image']")
            if image_element:
                image_element_url = None
                if image_element[0].has_attr("src"):
                    image_element_url = image_element[0]["src"]
                elif image_element[0].has_attr("content"):
                    image_element_url = image_element[0]["content"]
                elif image_element[0].has_attr("href"):
                    image_element_url = image_element[0]["href"]
                if image_element_url is not None:
                    annotation_target.image = image_element_url

        if annotation_target.image is None:
            image_element = bs_document.select("[itemProp='thumbnail'] > link[itemProp='url']")
            if image_element:
                image_element_url = None
                if image_element[0].has_attr("src"):
                    image_element_url = image_element[0]["src"]
                elif image_element[0].has_attr("content"):
                    image_element_url = image_element[0]["content"]
                elif image_element[0].has_attr("href"):
                    image_element_url = image_element[0]["href"]
                if image_element_url is not None:
                    annotation_target.image = image_element_url

        if annotation_target.image is None:
            image_element = bs_document.select("[itemProp='thumbnailUrl']")
            if image_element:
                image_element_url = None
                if image_element[0].has_attr("src"):
                    image_element_url = image_element[0]["src"]
                elif image_element[0].has_attr("content"):
                    image_element_url = image_element[0]["content"]
                elif image_element[0].has_attr("href"):
                    image_element_url = image_element[0]["href"]
                if image_element_url is not None:
                    annotation_target.image = image_element_url

        if annotation_target.title is None:
            name_element = bs_document.select("[itemProp='name']")
            if name_element:
                name = None

                if name_element[0].has_attr("content"):
                    name = name_element["content"]

                if name is not None:
                    annotation_target.title = name

        return True
