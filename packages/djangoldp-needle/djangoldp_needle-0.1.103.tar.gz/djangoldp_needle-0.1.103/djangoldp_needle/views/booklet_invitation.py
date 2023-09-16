import json

from djangoldp.views import LDPViewSet
from django.conf import settings
from djangoldp_account.models import LDPUser

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from ..models import Booklet, BookletContributor


class BookletInvitationViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        booklet = Booklet.objects.get(pk=kwargs['pk'])

        user_is_owner = BookletContributor.objects.filter(
            booklet=booklet,
            user=request.user,
            role__in=[BookletContributor.ROLE_OWNER, BookletContributor.ROLE_ADMIN]
        ).count() > 0

        if not user_is_owner:
            raise NotFound()
        try:
            target = LDPUser.objects.get(email=request.data['email'])
        except LDPUser.DoesNotExist as e:
            raise ValidationError(detail="Invalid email")

        target_is_contributor = BookletContributor.objects.filter(
            booklet=booklet,
            user=target,
        ).count() > 0
        if target_is_contributor:
            raise ValidationError(detail="Target exist")

        contributor = BookletContributor(
            booklet=booklet,
            user=target,
            role=BookletContributor.ROLE_VISIT
        )
        contributor.save()

        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(booklet)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

