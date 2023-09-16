from django.db import IntegrityError
from djangoldp.views import LDPViewSet
from rest_framework.exceptions import ValidationError


class AnnotationIntersectionReadViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        try:
            return super(AnnotationIntersectionReadViewset, self).create(request, args=args, kwargs=kwargs)
        except IntegrityError as e:
            raise ValidationError(detail="Annotation already exist for user")

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()

        qs\
            .select_related('annotation')\
            .select_related('creator')

        return qs
