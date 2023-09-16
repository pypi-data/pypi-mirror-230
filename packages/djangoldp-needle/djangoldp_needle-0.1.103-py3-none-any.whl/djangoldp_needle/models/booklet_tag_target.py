from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from djangoldp.models import Model
from . import BookletTag
from django.conf import settings

class BookletTagTarget(Model):
    tag = models.ForeignKey(
        BookletTag,
        null=True,
        on_delete=models.SET_NULL,
        related_name='targets'
    )
    target = models.CharField(max_length=4096)
    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                null=True,
                                on_delete=models.SET_NULL
                                )

    class Meta(Model.Meta):
        rdf_type = 'hd:booklet_tag'
        #auto_author = 'creator'
        #rdf_context = 'https://www.w3.org/ns/anno.jsonld'
        constraints = [
            models.UniqueConstraint(
                fields=["tag", "target"], name="unique_tag_target"
            )
        ]

@receiver(post_delete, sender=BookletTagTarget)
@transaction.atomic
def post_delete_target(sender, instance,  **kwargs):
    if Model.is_external(instance):
        return

    BookletTag.objects.filter(
        targets=None
    ).delete()
