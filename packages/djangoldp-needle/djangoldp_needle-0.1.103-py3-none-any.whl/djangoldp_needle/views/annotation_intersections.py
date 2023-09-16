from django.core.exceptions import SuspiciousOperation
from django.db.models import OuterRef, Count, Subquery
from djangoldp.serializers import LDPSerializer
from djangoldp.views import LDPViewSet
from rest_framework import serializers
import base64

from ..models import AnnotationTarget, Annotation

class AnnotationIntersectionsViewset(LDPViewSet):
    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return super().get_queryset()

        targets = self.request.data['targets']
        if not isinstance(targets, list):
            targets = [targets]

        res = Annotation\
            .objects \
            .select_related('target') \
            .select_related('creator') \
            .prefetch_related('tags') \
            .prefetch_related('booklets') \
            .annotate(yarn_count=Count('creator__yarn'))\
            .filter(target__target__in=targets, yarn_count__gt=1)\
            .exclude(creator=self.request.user)\
            .order_by(
            "creation_date")

        return res
