from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from djangoldp.models import Model
from djangoldp.serializers import LDPSerializer
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.dispatch import receiver

from . import BookletContributor, Booklet
from ..permissions import BookletContributorPendingPermissions

class BookletContributorPendingSerializer(LDPSerializer):
    with_cache = False

# Pending invitation when user does not exist
class BookletContributorPending(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    booklet_from = models.ForeignKey(Booklet,
        related_name='booklet_pending_from',
        null=True,
       on_delete=models.SET_NULL
    )
    booklet_to_email = models.CharField(max_length=255)

    @classmethod
    def get_serializer_class(cls):
        return BookletContributorPendingSerializer

    class Meta(Model.Meta):
        rdf_type = 'hd:booklet_contributor_pending'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        authenticated_perms = ['add']
        serializer_fields = ['@id', 'creation_date', 'booklet_from', 'booklet_to_email']
        constraints = [
            models.UniqueConstraint(
                fields=["booklet_from", "booklet_to_email"], name="unique_contributor_pending_contact_to_email"
            ),
        ]
        permission_classes = [BookletContributorPendingPermissions]

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_find_matching_emails_contributor_pending(sender, instance, created, **kwargs):
    if created and not Model.is_external(instance):
        contributors = BookletContributorPending.objects.filter(booklet_to_email=instance.email).all()
        if len(contributors) == 0:
            return
        for contributor_pending in contributors:
            contributor = BookletContributor(
                booklet=contributor_pending.booklet_from,
                user=instance,
                role=BookletContributor.ROLE_VISIT
            )
            contributor.save()

            contributor_pending.delete()
