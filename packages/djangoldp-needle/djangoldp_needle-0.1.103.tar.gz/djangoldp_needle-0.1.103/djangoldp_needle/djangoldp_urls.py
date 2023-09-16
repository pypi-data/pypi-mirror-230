from django.conf import settings
from django.conf.urls import url
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .models import Annotation, Tag, AnnotationTarget, AnnotationIntersectionRead, ContactMessage, \
    Booklet, NeedleUserFollow, Avatar, NeedleUserContact, NeedleUserContactPending, BookletContributor, \
    BookletContributorPending, BookletTag, BookletTagTarget, UserMailChangeToken
from .views import AnnotationViewset, AnnotationTargetViewset, TagViewset, AnnotationIntersectionReadViewset, \
    ContactMessageView, BookletViewset, BookletInvitationViewset, BookletQuitViewset, NeedleUserFollowViewset, \
    AnnotationIntersectionsViewset, \
    avatars_animals_list, avatars_quality_list, AvatarViewset, NeedleUserContactViewset, validate_invitation, \
    NeedleUserContactPendingViewset, BookletContributorPendingViewset, booklet_bulk_delete, BookletContributorViewset, \
    BookletBulkDeleteViewset, NeedleUserContactResendViewset, BookletTagAllViewset, BookletTagViewset, \
    BookletTagTargetAllViewset, BookletTagTargetViewset, UserMailChangeTokenViewset, validate_change_email_token

urlpatterns = [
    url(r'^booklets/', BookletViewset.urls(model_prefix="booklet", model=Booklet)),
    url(r'^bookletcontributors/', BookletContributorViewset.urls(model_prefix="bookletcontributors", model=BookletContributor)),
    url(r'^bookletcontributorspending/', BookletContributorPendingViewset.urls(model_prefix="bookletcontributorspending", model=BookletContributorPending)),
    path(r'booklettags/<pk>/', BookletTagAllViewset.as_view({'get': 'retrieve'}, model=BookletTag)),
    url(r'^booklettags/', BookletTagAllViewset.as_view({'get': 'list', 'post': 'create'}, model=BookletTag)),
    path(r'booklettagtargets/<pk>/', BookletTagTargetAllViewset.as_view({'get': 'retrieve', 'delete': 'destroy'}, model=BookletTagTarget)),
    url(r'^booklettagtargets/', BookletTagTargetAllViewset.as_view({'get': 'list', 'post': 'create'}, model=BookletTagTarget)),
    path('booklets/<pk>/invitation/', BookletInvitationViewset.as_view({'post': 'create'}, model=Booklet)),
    path('booklets/<pk>/quit/', BookletQuitViewset.as_view({'post': 'create'}, model=Booklet)),
    path('booklets/<pk>/bulk_delete/', BookletBulkDeleteViewset.as_view({'post': 'create'}, model=Booklet)),
    path('booklets/<pk>/tags/', BookletTagViewset.as_view({'get': 'list'}, model=BookletTag)),
    path('booklets/<pk>/tagtargets/', BookletTagTargetViewset.as_view({'get': 'list'}, model=BookletTagTarget)),
    url(r'^annotations/', AnnotationViewset.urls(model_prefix="annoations", model=Annotation)),
    url(r'^annotationtargets/', AnnotationTargetViewset.urls(model_prefix="annotationtarget", model=AnnotationTarget)),
    url(r'^users/(?P<slug>[\w\-\.]+)/annotation_intersection_read/', AnnotationIntersectionReadViewset.urls(model_prefix="annotationintersectionread", model=AnnotationIntersectionRead)),
    url(r'^annotationintersectionreads/', AnnotationIntersectionReadViewset.urls(model_prefix="annotationintersectionread", model=AnnotationIntersectionRead)),
    path('annotationintersections/',
        AnnotationIntersectionsViewset.as_view({'post': 'list'}, model=Annotation)),
    url(r'^users/(?P<slug>[\w\-\.]+)/yarn/', AnnotationViewset.urls(model_prefix="yarn", model=Annotation)),
    url(r'^users/(?P<slug>[\w\-\.]+)/tags', TagViewset.urls(model_prefix="tags", model=Tag)),
    url(r'^users/(?P<slug>[\w\-\.]+)/avatar', AvatarViewset.as_view({'get': 'retrieve'},  model=Avatar)),
    url(r'^contact_messages/', ContactMessageView.as_view({'post': 'create'},  model=ContactMessage)),
    url(r'^needleuserfollow/', NeedleUserFollowViewset.urls(model=NeedleUserFollow)),
    url(r'^needleusercontacts/', NeedleUserContactViewset.urls(model=NeedleUserContact)),
    url(r'^needleusercontacts/(?P<pk>[\w\-\.]+)/resend/', NeedleUserContactResendViewset.as_view({'post': 'create'},  model=NeedleUserContact)),
    url(r'^needleusercontactpending/', NeedleUserContactPendingViewset.urls(model=NeedleUserContactPending)),
    path('needleusercontact_validate/<token>', csrf_exempt(validate_invitation)),
    url(r'^avatars_animals_list/$', csrf_exempt(avatars_animals_list)),
    url(r'^avatars_quality_list/$', csrf_exempt(avatars_quality_list)),
    path('usermailchangetoken_validate/<token>', csrf_exempt(validate_change_email_token)),
    url(r'^usermailchangetokens/', UserMailChangeTokenViewset.urls(model=UserMailChangeToken)),
]
