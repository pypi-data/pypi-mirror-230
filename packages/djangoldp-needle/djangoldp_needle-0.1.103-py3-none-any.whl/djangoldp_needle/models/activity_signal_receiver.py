import datetime

from djangoldp.models import Model
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings

from . import Annotation
from . import AnnotationTarget
from . import NeedleUserProfile
from . import Avatar
from . import NeedleActivity, ACTIVITY_TYPE_NEW_USER, \
    ACTIVITY_TYPE_FIRST_ANNOTATION_WITH_CONNECTIONS, ACTIVITY_TYPE_FIRST_ANNOTATION_WITHOUT_CONNECTIONS
from ..settings import get_avatar_level
import random

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_user(sender, instance, created, **kwargs):
    # print("UPDATE USER: {0} with id {1}".format(instance, instance.pk))
    if not hasattr(instance, "needle_user_profiles") and not Model.is_external(instance):
        new_needle_user_profile = NeedleUserProfile(creator=instance,
                                                    activity_crossed_yarn_last_date=datetime.date.today(),
                                                    activity_followed_yarn_last_date=datetime.date.today(),
                                                    activity_pads_last_date=datetime.date.today(),
                                                    name=""
                                                    )
        new_needle_user_profile.save()
    if not hasattr(instance, "avatar") and not Model.is_external(instance):
        new_needle_user_profile = Avatar(creator=instance,
                                         name_avatar=get_avatar_level(1),
                                         name_number=random.randint(1111111, 9999999)
                                )
        new_needle_user_profile.save()

    if created and not Model.is_external(instance):
        # print("NEW USER: {0} with id {1}".format(instance, instance.pk))
        create_welcome_needle_activity(instance);

@receiver(post_save, sender=Annotation)
def post_save_annotation_avatar(sender, instance, created, **kwargs):
    if created and not Model.is_external(instance):
        if instance.creator.yarn.count() > 3:
            avatarLevel1 = get_avatar_level(1)
            creator_avatar = instance.creator.avatar
            if creator_avatar.name_avatar == avatarLevel1:
                creator_avatar.name_avatar = get_avatar_level(2)
                creator_avatar.save()

@receiver(post_save, sender=Annotation)
def post_save_annotation(sender, instance, created, **kwargs):
    # print("UPDATE ANNOTATION: {0} with id {1}".format(instance, instance.pk))
    if created and not Model.is_external(instance):
        # print("NEW ANNOTATION: {0} with id {1}".format(instance, instance.pk))
        # retourne les annotation avec la même target
        result_annotation_same_target = Annotation.objects.filter(target=instance.target)
        # retourne les annotations du même utilisateur
        result_annotation_current_user = Annotation.objects.filter(creator=instance.creator)
        # Première annotation ?
        if result_annotation_current_user.count() == 1:
            # Première annotation target ?
            if result_annotation_same_target.count() == 1:
                create_first_annotation_activity_first_annotation_without_connections(instance)
            else:
                create_first_annotation_activity_first_annotation_with_connections(instance)

        else:
            # Première annotation target ?
            if result_annotation_same_target.count() == 1:

                result_needle_activity = \
                    NeedleActivity.objects.filter(creator=instance.creator,
                                                  activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITHOUT_CONNECTIONS)
                # L'utilisateur a-t'il déjà reçu une notification de ce type ?
                if result_needle_activity.count() == 0:
                    create_first_annotation_activity_annotation_without_connections(instance)
            else:
                result_needle_activity = \
                    NeedleActivity.objects.filter(creator=instance.creator,
                                                  activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITH_CONNECTIONS)
                # L'utilisateur a-t'il déjà reçu une notification de ce type ?
                if result_needle_activity.count() == 0:
                    create_first_annotation_activity_annotation_with_connections(instance)


@receiver(post_save, sender=AnnotationTarget)
def post_save_annotation_target(sender, instance, created, **kwargs):
    pass
    # print("UPDATE ANNOTATION TARGET: {0} with id {1}".format(instance, instance.pk))
    # if created and not Model.is_external(instance):
    #     print("NEW ANNOTATION TARGET: {0} with id {1}".format(instance, instance.pk))



@receiver(pre_save, sender=Annotation)
def pre_save_annotation(sender, instance, **kwargs):
    if not Model.is_external(instance):
        if instance.annotation_date is None :
            instance.annotation_date = datetime.datetime.now()
    pass
    # print("UPDATE ANNOTATION TARGET: {0} with id {1}".format(instance, instance.pk))
    # if created and not Model.is_external(instance):
    #     print("NEW ANNOTATION TARGET: {0} with id {1}".format(instance, instance.pk))



def create_first_annotation_activity_annotation_with_connections(annotation):
    first_annotation_activity = NeedleActivity(activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITH_CONNECTIONS,
                                               title="Grâce à votre fiche, vous croisez déjà d'autres personnes",
                                               content="Découvrez leurs Fils pour faire de **nouvelles trouvailles**.",
                                               creator=annotation.creator)
    first_annotation_activity.save()


def create_first_annotation_activity_annotation_without_connections(annotation):
    new_annotation_target_activity = NeedleActivity(activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITHOUT_CONNECTIONS,
                                                    title="Votre fiche sort de l'ordinaire",
                                                    content="Vous êtes la **première personne** à l'avoir ajoutée à votre Fil.\nAjoutez-en d'autres pour augmenter vos chances de croiser les Fils d'autres personnes, ou bien parcourez les carnets publics existants.",
                                                    creator=annotation.creator)
    new_annotation_target_activity.save()


def create_first_annotation_activity_first_annotation_with_connections(annotation):
    first_annotation_activity = NeedleActivity(activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITH_CONNECTIONS,
                                               title="Grâce à votre première fiche, vous croisez déjà d'autres personnes",
                                               content="Découvrez leurs Fils pour faire de **nouvelles trouvailles**.",
                                               creator=annotation.creator)
    first_annotation_activity.save()


def create_first_annotation_activity_first_annotation_without_connections(annotation):
    new_annotation_target_activity = NeedleActivity(activity_type=ACTIVITY_TYPE_FIRST_ANNOTATION_WITHOUT_CONNECTIONS,
                                                    title="Votre première fiche sort de l'ordinaire",
                                                    content="Vous êtes la **première personne** à l'avoir ajoutée à votre Fil.\nAjoutez-en d'autres pour augmenter vos chances de croiser les Fils d'autres personnes, ou bien parcourez les carnets publics existants.",
                                                    creator=annotation.creator)
    new_annotation_target_activity.save()

def create_welcome_needle_activity(user):
    welcome = NeedleActivity(activity_type=ACTIVITY_TYPE_NEW_USER, title="Ajoutez une première Fiche à votre Fil",
                             content="Quelles sont les dernières trouvailles marquantes que vous ayez faites sur le web ?",
                             creator=user)
    welcome.save()
