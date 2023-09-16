from django.conf import settings
from django.db import models
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer

from ..permissions import AvatarPermissions

class AvatarSerializer(LDPSerializer):
    def to_representation(self, obj):
        rep = super().to_representation(obj)
        avatarConfig = getattr(settings, 'NEEDLE_AVATARS', {})

        try:
            rep['avatar_url'] = avatarConfig[rep['name_avatar']]['image']
        except:
            rep['avatar_url'] = None

        rep['full_name'] = obj.get_full_name()

        return rep

class Avatar(Model):
    creator = models.OneToOneField(settings.AUTH_USER_MODEL,
                                   related_name='avatar',
                                   on_delete=models.CASCADE,
                                   primary_key=True
                                   )

    name_number = models.CharField(max_length=255)
    name_avatar = models.CharField(max_length=255)
    name_quality = models.CharField(max_length=255, null=True)

    name = models.CharField(max_length=16)

    @classmethod
    def get_serializer_class(cls):
        return AvatarSerializer

    def get_full_name(self):
        avatarConfig = getattr(settings, 'NEEDLE_AVATARS', {})
        return (avatarConfig[self.name_avatar]['name'] or '')+ " " + (self.name_quality or '') + "#" + str(self.name_number)

    class Meta(Model.Meta):
        rdf_type = 'hd:avatar'
        owner_field = 'creator'
        authenticated_perms = ['view']
        anonymous_perms = ['view']
        owner_perms = ['view', 'change']
        permission_classes = [AvatarPermissions]