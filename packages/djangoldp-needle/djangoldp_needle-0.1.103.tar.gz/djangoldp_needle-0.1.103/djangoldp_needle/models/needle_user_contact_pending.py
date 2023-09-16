from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.dispatch import receiver

from . import NeedleUserContact
from ..permissions import NeedleUserContactPendingPermissions

class NeedleUserContactPendingSerializer(LDPSerializer):
    with_cache = False

# Pending invitation when user does not exist
class NeedleUserContactPending(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    contact_from = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='contact_pending_from',
        null=True,
       on_delete=models.SET_NULL
    )
    contact_to_email = models.CharField(max_length=255)

    @classmethod
    def get_serializer_class(cls):
        return NeedleUserContactPendingSerializer

    class Meta(Model.Meta):
        rdf_type = 'hd:needle_user_contact_pending'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        authenticated_perms = ['add']
        auto_author = 'contact_from'
        owner_field = 'contact_from'
        owner_perms = ['view', 'delete']
        serializer_fields = ['@id', 'creation_date', 'contact_from', 'contact_to_email']
        constraints = [
            models.UniqueConstraint(
                fields=["contact_from", "contact_to_email"], name="unique_contact_to_email"
            ),
        ]
        permission_classes = [NeedleUserContactPendingPermissions]

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_find_matching_emails(sender, instance, created, **kwargs):
    if created and not Model.is_external(instance):
        contacts = NeedleUserContactPending.objects.filter(contact_to_email=instance.email).all()
        if len(contacts) == 0:
            return
        for contact_pending in contacts:
            contact = NeedleUserContact(
                contact_from=contact_pending.contact_from,
                contact_to=instance
            )
            contact.save()
            contact_reverse = NeedleUserContact(
                contact_from=contact.contact_to,
                contact_to=contact.contact_from
            )
            contact_reverse.save()

            # Auto validate invitation
            contact.invitation_token = None
            contact.save()
            contact_reverse.invitation_token = None
            contact_reverse.save()

            contact_pending.delete()
