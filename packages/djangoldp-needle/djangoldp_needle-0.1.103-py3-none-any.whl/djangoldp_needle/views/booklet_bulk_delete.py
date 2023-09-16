import json

from djangoldp.views import LDPViewSet
from django.conf import settings
from djangoldp_account.models import LDPUser

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from ..models import Booklet, BookletContributor, Annotation


class BookletBulkDeleteViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        obj = get_object_or_404(Booklet.objects, pk=kwargs['pk'])

        # Permission test
        try:
            booklet_contributor = obj.contributors.filter(
                user=self.request.user,
                role__in=(BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_OWNER, BookletContributor.ROLE_ADMIN)
            ).get()
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        annotations = obj.annotations.filter(
            target__target=request.data['target']
        ).all()
        for annotation in annotations:
            obj.annotations.remove(annotation)

        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(obj)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_200_OK, headers=headers)

