from django.conf import settings
from django.db import models
from djangoldp.models import Model
from . import Tag
from ..permissions import NeedleUserFollowPermissions


class NeedleUserFollow(Model):
    follow_from = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='followed',
                                null=True,
                               on_delete=models.SET_NULL
                                )
    follow_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                related_name='followers',
                null=True,
                on_delete=models.SET_NULL
            )
    title = models.CharField(max_length=160, blank=False)
    description = models.TextField(null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta(Model.Meta):
        rdf_type = 'hd:annotation'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        authenticated_perms = ['add']
        auto_author = 'follow_from'
        owner_field = 'follow_from'
        owner_perms = ['view', 'change', 'delete']
        constraints = [
            models.UniqueConstraint(
                fields=["follow_from", "follow_to"], name="unique_follow"
            )
        ]
        permission_classes = [NeedleUserFollowPermissions]