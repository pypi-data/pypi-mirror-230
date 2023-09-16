from django.conf import settings
from django.db import models
from djangoldp.models import Model

from ..permissions import NeedleUserProfilePermissions

class NeedleUserProfile(Model):
    creator = models.OneToOneField(settings.AUTH_USER_MODEL,
                                   related_name='needle_user_profile',
                                   on_delete=models.CASCADE,
                                   primary_key=True
                                   )

    activity_crossed_yarn_last_date = models.DateField()
    activity_followed_yarn_last_date = models.DateField()
    activity_pads_last_date = models.DateField()

    name = models.CharField(max_length=16)

    class Meta(Model.Meta):
        rdf_type = 'hd:user_profile'
        owner_field = 'creator'
        owner_perms = ['view', 'change']
        permission_classes = [NeedleUserProfilePermissions]