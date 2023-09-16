from django.conf import settings
from django.db import models
from djangoldp.models import Model
from . import Tag, Annotation
from ..permissions import AnnotationIntersectionReadPermissions


class AnnotationIntersectionRead(Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='annotation_intersection_read',
                                null=True,
                               on_delete=models.SET_NULL
                                )
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta(Model.Meta):
        rdf_type = 'hd:annotation_intersection_read'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        depth = 1
        anonymous_perms = []
        authenticated_perms = ['add']
        auto_author = 'creator'
        owner_field = 'creator'
        owner_perms = ['view', 'delete']
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "annotation"], name="unique_creator_annotation"
            )
        ]
        permission_classes = [AnnotationIntersectionReadPermissions]