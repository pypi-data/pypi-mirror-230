from django.conf import settings
from django.db import models
from djangoldp.models import Model
from djangoldp.permissions import LDPPermissions
from djangoldp.serializers import LDPSerializer, ContainerSerializer
from djangoldp.views import LDPViewSet

from .annotation_target import AnnotationTarget
from . import Tag
from ..permissions import AnnotationPermissions

class AnnotationSerializer(LDPSerializer):
    annotationTargetSerializer = None

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if hasattr(obj, "local_intersection_after"):
            rep['local_intersection_after'] = obj.local_intersection_after
        if hasattr(obj, "local_intersection_before"):
            rep['local_intersection_before'] = obj.local_intersection_before

        target = obj.target
        if target is not None:
            if self.annotationTargetSerializer is None: # Force depth 1 serialization for target only
                serializer_generator = LDPViewSet(model=AnnotationTarget,
                                                  lookup_field=Model.get_meta(AnnotationTarget, 'lookup_field', 'pk'),
                                                  permission_classes=Model.get_meta(AnnotationTarget,
                                                                                    'permission_classes',
                                                                                    [LDPPermissions]),
                                                  )
                self.annotationTargetSerializer = serializer_generator.build_read_serializer()(context=self.context)
            rep['target'] = self.annotationTargetSerializer.to_representation(target)

        return rep

class Annotation(Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='yarn',
                                null=True,
                               on_delete=models.SET_NULL
                                )
    creation_date = models.DateTimeField(auto_now_add=True)
    annotation_date = models.DateTimeField(null=True)
    target = models.ForeignKey(AnnotationTarget, null=True, on_delete=models.SET_NULL, related_name='annotations')
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(null=True)

    @classmethod
    def get_serializer_class(cls):
        return AnnotationSerializer

    class Meta(Model.Meta):
        rdf_type = 'hd:annotation'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        authenticated_perms = ['add', 'view']
        auto_author = 'creator'
        owner_field = 'creator'
        owner_perms = ['view', 'delete', 'change']
        serializer_fields = ['@id', 'creator', 'creation_date', 'annotation_date', 'target', 'tags', 'description', 'booklets']
        permission_classes = [AnnotationPermissions]