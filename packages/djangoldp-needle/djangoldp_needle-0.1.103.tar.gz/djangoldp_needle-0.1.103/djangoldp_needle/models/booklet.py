from django.db import models
from djangoldp.models import Model
from . import Annotation, Tag
from ..permissions import BookletPermissions


class Booklet(Model):
    annotations = models.ManyToManyField(Annotation, related_name="booklets")
    title = models.CharField(max_length=160)
    abstract = models.CharField(max_length=4096, null=True)
    accessibility_public = models.BooleanField()
    collaboration_allowed = models.BooleanField()
    cover = models.IntegerField()

    class Meta(Model.Meta):
        rdf_type = 'hd:booklet'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        owner_perms = []
        authenticated_perms = []
        anonymous_perms = []
        permission_classes = [BookletPermissions]