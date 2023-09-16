from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from djangoldp.views import LDPViewSet
from djangoldp_account.models import LDPUser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status

from ..models import NeedleUserFollow, NeedleUserContact, BookletContributor, Booklet
from django.core.mail import send_mail
from django.template import loader


class BookletContributorPendingViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        if LDPUser.objects.filter(email=request.data['booklet_to_email']).count() > 0:
            return Response({'E-mail': [
                'Cette personne existe déjà sur Needle']},
                status=status.HTTP_400_BAD_REQUEST)

        if BookletContributor.objects.filter(user=request.user, booklet__urlid=request.data['booklet_from']['@id'],
                                             role=BookletContributor.ROLE_OWNER).count() == 0:
            return Response({'Booklet': [
                'Vous devez être propriétaire du carnet']},
                status=status.HTTP_400_BAD_REQUEST)

        return super().create(request)

    def perform_create(self, serializer, **kwargs):
        res = super().perform_create(serializer)
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', False)

        booklet_id = self.request.data['booklet_from']['@id']
        booklet_url = settings.INSTANCE_DEFAULT_CLIENT + "/carnets/voir/@" + booklet_id + "@";

        if email_from:
            from_email = self.request.user.email
            from_url = settings.INSTANCE_DEFAULT_CLIENT + "/@" + settings.BASE_URL + "/users/" + self.request.user.username + "/@";

            template_parameters = {
                'from_name': self.request.user.avatar.get_full_name(),
                'from_email': from_email,
                'from_url': from_url,
                'link': settings.BASE_URL + '/auth/register/',
                'booklet': res.booklet_from.title,
                'booklet_id': booklet_id,
                'booklet_url': booklet_url
            }
            message = loader.render_to_string(
                'emails/booklet_pending.txt',
                template_parameters
            )

            html_message = loader.render_to_string(
                'emails/booklet_pending.html',
                template_parameters
            )

            send_mail(
                '[Needle] Invitation à participer à un carnet',
                message,
                email_from,
                [res.booklet_to_email],
                html_message=html_message
            )

        return res
