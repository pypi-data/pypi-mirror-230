from djangoldp.serializers import LDPSerializer
from djangoldp.views import LDPViewSet
from rest_framework.exceptions import  PermissionDenied
from rest_framework.generics import get_object_or_404

from . import get_booklet_user_pk, qs_booklet_user
from ..models import Booklet, BookletContributor, BookletTag, BookletTagTarget


class BookletTagTargetAllViewset(LDPViewSet):
   def get_object(self):
      user_booklets = qs_booklet_user(self.request.user)
      obj = get_object_or_404(
         BookletTagTarget.objects.filter(
            tag__booklet__in=user_booklets
         ),
         pk=self.kwargs['pk']
      )

      self.check_object_permissions(self.request, obj)

      return obj

   def get_queryset(self, *args, **kwargs):
      return BookletTagTarget.objects.none()


   def has_tag_moderator_permission(self, user, tag_urlid):
      if user.is_anonymous:
         return False

      return BookletContributor \
         .objects \
         .filter(
         user=user,
         booklet__tags__urlid=tag_urlid,
         role__in=(
         BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER)
      ) \
         .count() > 0

   def is_safe_create(self, user, validated_data, *args, **kwargs):
      return self.has_tag_moderator_permission(user, validated_data['tag']['urlid'])

   def create(self, request, *args, **kwargs):
      return super().create(request)

   def perform_destroy(self, instance):
      if not self.has_tag_moderator_permission(self.request.user, instance.tag.urlid):
         raise PermissionDenied()
      instance.delete()

class BookletTagTargetViewset(LDPViewSet):
   def get_queryset(self, *args, **kwargs):
      related_booklet= get_booklet_user_pk(self.request.user, self.kwargs['pk'])
      return BookletTagTarget.objects.filter(tag__booklet=related_booklet)