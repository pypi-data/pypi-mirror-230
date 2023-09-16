from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from djangoldp.serializers import LDPSerializer
from djangoldp_account.models import LDPUser, Account
from djangoldp.models import Model

from . import NeedleUserContact, Annotation, Tag, Avatar, AnnotationIntersectionRead, ContactMessage, NeedleActivity, \
    NeedleUserFollow, NeedleUserProfile

def has_permisson_name(current_user, target_user):
    if current_user.is_anonymous:
        return False
    if current_user == target_user:
        return True
    return NeedleUserContact.objects.filter(contact_from=current_user, contact_to=target_user,
                                                             invitation_token=None).count() > 0

class UserSerializer(LDPSerializer):
    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if not isinstance(obj, LDPUser):
            return rep

        current_user = self.context['request'].user
        if not has_permisson_name(current_user, obj):
            del rep['last_name']
            del rep['first_name']
            del rep['name']
            del rep['email']
            rep['account']['picture'] = None
        return rep

# Monkey patching user to pass a custom serializer
@classmethod
def get_serializer_class_user(cls):
    return UserSerializer

LDPUser.get_serializer_class = get_serializer_class_user

@receiver(pre_delete, sender=LDPUser)
@transaction.atomic
def pre_delete_user(sender, instance,  **kwargs):
    if Model.is_external(instance):
        return

    # Hook to manage reverse foreign key reverse remove
    Annotation.objects.filter(creator=instance).delete()
    Tag.objects.filter(creator=instance).delete()
    Avatar.objects.filter(creator=instance).delete()
    AnnotationIntersectionRead.objects.filter(creator=instance).delete()
    ContactMessage.objects.filter(target=instance).delete()
    ContactMessage.objects.filter(source=instance).delete()
    NeedleActivity.objects.filter(creator=instance).delete()
    NeedleUserFollow.objects.filter(follow_from=instance).delete()
    NeedleUserFollow.objects.filter(follow_to=instance).delete()
    NeedleUserProfile.objects.filter(creator=instance).delete()


class AccountSerializer(LDPSerializer):
    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if not isinstance(obj, Account):
            return rep

        current_user = self.context['request'].user
        if not has_permisson_name(current_user, obj.user):
            rep['picture'] = None
        return rep

# Monkey patching account to pass a custom serializer
@classmethod
def get_serializer_class_account(cls):
    return AccountSerializer

Account.get_serializer_class = get_serializer_class_account

