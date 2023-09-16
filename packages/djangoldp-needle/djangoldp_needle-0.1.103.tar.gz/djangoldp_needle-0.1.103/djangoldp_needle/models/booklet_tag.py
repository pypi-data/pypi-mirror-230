from django.db import models
from djangoldp.models import Model
from . import Booklet
from ..permissions import BookletPermissions


class BookletTag(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    booklet = models.ForeignKey(Booklet,
                                related_name='tags',
                                null=True,
                                on_delete=models.SET_NULL
                    )
    class Meta(Model.Meta):
        rdf_type = 'hd:booklet_tag'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "booklet"], name="unique_tag_name_booklet"
            )
        ]