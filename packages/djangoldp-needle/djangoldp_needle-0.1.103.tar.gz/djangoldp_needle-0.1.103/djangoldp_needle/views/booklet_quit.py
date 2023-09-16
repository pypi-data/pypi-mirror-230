import json

from django.core.exceptions import ObjectDoesNotExist
from djangoldp.views import LDPViewSet
from django.conf import settings
from djangoldp_account.models import LDPUser

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from ..models import Booklet, BookletContributor


class BookletQuitViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        try:
            booklet = Booklet.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotFound()

        try:
            booklet_contributor = BookletContributor.objects.get(
                booklet=booklet,
                user=request.user
            )
        except ObjectDoesNotExist:
            raise NotFound()

        booklet_contributor.delete()

        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(booklet)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_200_OK, headers=headers)

