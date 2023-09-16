from django.conf import settings
from django.db import models
from django.dispatch import receiver
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer

from ..permissions import NeedleUserContactPermissions
from django.db.models.signals import pre_save, post_save
import uuid

class NeedleUserContactSerializer(LDPSerializer):
    with_cache = False

class NeedleUserContact(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    contact_from = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='contact_from',
        null=True,
       on_delete=models.SET_NULL
    )
    contact_to = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='contact_to',
        null=True,
        on_delete=models.SET_NULL
    )
    invitation_token = models.CharField(max_length=255, null=True)
    message = models.TextField(null=True)

    @property
    def has_invitation_token(self):
        return self.invitation_token is not None

    @classmethod
    def get_serializer_class(cls):
        return NeedleUserContactSerializer

    class Meta(Model.Meta):
        rdf_type = 'hd:needle_user_contact'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        authenticated_perms = ['add']
        auto_author = 'contact_from'
        owner_field = 'contact_from'
        owner_perms = ['view', 'delete']
        serializer_fields = ['@id', 'creation_date', 'contact_from', 'contact_to', 'has_invitation_token', 'message']
        constraints = [
            models.UniqueConstraint(
                fields=["contact_from", "contact_to"], name="unique_contact"
            ),
            models.UniqueConstraint(
                fields=["invitation_token"], name="unique_contact_invitation"
            )
        ]
        permission_classes = [NeedleUserContactPermissions]


@receiver(post_save, sender=NeedleUserContact)
def post_save_generate_uuid_on_creation(sender, created, instance,  **kwargs):
    if created and not Model.is_external(instance):
        instance.invitation_token = uuid.uuid4()
        instance.save()