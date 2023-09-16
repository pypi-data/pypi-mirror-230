from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.template import loader
from djangoldp.views import LDPViewSet
from django.conf import settings

from ..models import UserMailChangeToken


class UserMailChangeTokenViewset(LDPViewSet):
    def perform_create(self, serializer, **kwargs):
        res = super().perform_create(serializer)
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', False)

        template_parameters = {
            'from_name': res.creator.avatar.get_full_name(),
            'link': settings.BASE_URL + '/usermailchangetoken_validate/' + str(res.token),
        }
        message = loader.render_to_string(
            'emails/user_mail_change.txt',
            template_parameters
        )

        html_message = loader.render_to_string(
            'emails/user_mail_change.html',
            template_parameters
        )

        send_mail(
            '[Needle] Changement de mail',
            message,
            email_from,
            [res.email],
            html_message=html_message
        )

def validate_change_email_token(request, *args, **kwargs):
    try :
        change_email = UserMailChangeToken.objects.get(token=kwargs['token'])
    except ObjectDoesNotExist:
        return HttpResponse('Le lien que vous avez suivi est invalide ou expiré', status=404)

    creator = change_email.creator
    creator.email = change_email.email
    creator.save()

    change_email.delete()

    return HttpResponsePermanentRedirect(settings.INSTANCE_DEFAULT_CLIENT)

