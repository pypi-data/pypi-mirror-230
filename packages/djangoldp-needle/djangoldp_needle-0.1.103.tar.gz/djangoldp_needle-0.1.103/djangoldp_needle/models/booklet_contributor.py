from django.conf import settings
from django.db import models
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer

from . import Booklet
from ..permissions import BookletContributorPermissions

class BookletContributor(Model):
    ROLE_VISIT = 'ROLE_VISIT'
    ROLE_CONTRIBUTOR = 'ROLE_CONTRIBUTOR'
    ROLE_MODERATOR = 'ROLE_MODERATOR'
    ROLE_ADMIN = 'ROLE_ADMIN'
    ROLE_OWNER = 'ROLE_OWNER'
    ROLE_CHOICES = [
        (ROLE_VISIT, 'ROLE_VISIT'),
        (ROLE_CONTRIBUTOR, 'ROLE_CONTRIBUTOR'),
        (ROLE_MODERATOR, 'ROLE_MODERATOR'),
        (ROLE_ADMIN, 'ROLE_ADMIN'),
        (ROLE_OWNER, 'ROLE_OWNER'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                      related_name='booklet_contributor',
                      on_delete=models.CASCADE
          )
    booklet = models.ForeignKey(Booklet,
                      related_name='contributors',
                      on_delete=models.CASCADE
          )
    role = models.CharField(max_length=160, choices=ROLE_CHOICES, default=ROLE_VISIT)

    class Meta(Model.Meta):
        rdf_type = 'hd:booklet_contributor'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        owner_perms = []
        authenticated_perms = []
        anonymous_perms = []
        permission_classes = [BookletContributorPermissions]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "booklet"], name="unique_booklet_contributor"
            )
        ]