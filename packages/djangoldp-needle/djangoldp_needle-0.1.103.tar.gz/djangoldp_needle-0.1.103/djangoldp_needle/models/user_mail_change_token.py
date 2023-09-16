import uuid
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer

class UserMailChangeTokenSerializer(LDPSerializer):
    with_cache = False

class UserMailChangeToken(Model):
    creator = models.OneToOneField(settings.AUTH_USER_MODEL,
                                   related_name='mail_change_token',
                                   on_delete=models.CASCADE,
                                   primary_key=True
                       )

    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    @classmethod
    def get_serializer_class(cls):
        return UserMailChangeTokenSerializer

    class Meta(Model.Meta):
        rdf_type = 'hd:mail_change_token'
        owner_field = 'creator'
        auto_author = 'creator'
        authenticated_perms = ['add']
        anonymous_perms = []
        owner_perms = ['view', 'delete']
        constraints = [
            models.UniqueConstraint(
                fields=["creator"], name="unique_creator_mail_change_token"
            )
        ]
        serializer_fields = ['@id', 'email']

@receiver(post_save, sender=UserMailChangeToken)
def post_save_mail_change_generate_uuid_on_creation(sender, created, instance,  **kwargs):
    if created and not Model.is_external(instance):
        instance.token = uuid.uuid4()
        instance.save()