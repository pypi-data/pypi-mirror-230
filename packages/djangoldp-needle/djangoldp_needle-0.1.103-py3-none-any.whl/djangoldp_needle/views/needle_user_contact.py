from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from djangoldp.views import LDPViewSet
from djangoldp_account.models import LDPUser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status

from ..models import NeedleUserFollow, NeedleUserContact
from django.core.mail import send_mail
from django.template import loader

class NeedleUserContactViewset(LDPViewSet):
    def create(self, request, *args, **kwargs):
        # Fetch target from email
        try:
            target_user = LDPUser.objects.get(email=request.data['contact_to_email'])
        except ObjectDoesNotExist:
            return Response({'E-mail': ['Cette personne n\'existe pas sur Needle. <solid-contact-button-add-invitation></solid-contact-button-add-invitation>']}, status=status.HTTP_400_BAD_REQUEST)

        if NeedleUserContact.objects.filter(contact_from=request.user, contact_to=target_user).count() > 0:
            return Response({'E-mail': ['Une invitation existe déjà pour cet utilisateur']},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data['contact_to'] = {
            '@id': target_user.urlid
        }

        return super().create(request)

    def perform_create(self, serializer, **kwargs):
        res = super().perform_create(serializer)
        send_invitation_mail(res)

        return res

def send_invitation_mail(contact):
    email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', False)

    if email_from:
        template_parameters = {
            'from_name': contact.contact_from.avatar.get_full_name(),
            'from_email': contact.contact_from.email,
            'link': settings.BASE_URL + '/needleusercontact_validate/' + str(contact.invitation_token),
            'message': contact.message
        }
        message = loader.render_to_string(
            'emails/invitation.txt',
            template_parameters
        )

        html_message = loader.render_to_string(
            'emails/invitation.html',
            template_parameters
        )

        send_mail(
            '[Needle] Nouvelle demande de contact',
            message,
            email_from,
            [contact.contact_to.email],
            html_message=html_message
        )

def validate_invitation(request, *args, **kwargs):
    try :
        contact = NeedleUserContact.objects.get(invitation_token=kwargs['token'])
    except ObjectDoesNotExist:
        return HttpResponse('Le lien que vous avez suivi est invalide ou expiré', status=404)

    contact.invitation_token = None
    contact.save()

    try:
        reverse_contact = NeedleUserContact.objects.get(contact_from=contact.contact_to, contact_to=contact.contact_from)
    except ObjectDoesNotExist:
        reverse_contact = NeedleUserContact(contact_from=contact.contact_to, contact_to=contact.contact_from)
    reverse_contact.save()
    reverse_contact.invitation_token = None
    reverse_contact.save()

    return HttpResponsePermanentRedirect(settings.INSTANCE_DEFAULT_CLIENT)

