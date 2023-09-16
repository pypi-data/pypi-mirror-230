from djangoldp.views import LDPViewSet
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from . import send_invitation_mail


class NeedleUserContactResendViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        contact = self.get_object()
        if contact.contact_from != request.user:
            raise PermissionDenied()

        if contact.invitation_token == None:
            raise PermissionDenied()

        send_invitation_mail(contact)

        return Response(status=status.HTTP_204_NO_CONTENT)
