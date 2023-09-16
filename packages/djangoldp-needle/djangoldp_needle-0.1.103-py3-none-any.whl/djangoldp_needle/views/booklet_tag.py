from djangoldp.serializers import LDPSerializer
from djangoldp.views import LDPViewSet
from rest_framework.generics import get_object_or_404

from . import get_booklet_user_pk, qs_booklet_user
from ..models import Booklet, BookletContributor, BookletTag


class BookletTagAllViewset(LDPViewSet):
   def get_queryset(self, *args, **kwargs):
      return BookletTag.objects.none()

   def get_object(self):
      user_booklets = qs_booklet_user(self.request.user)
      obj = get_object_or_404(
         BookletTag.objects.filter(
            booklet__in=user_booklets
         ),
         pk=self.kwargs['pk']
      )

      self.check_object_permissions(self.request, obj)

      return obj

   def is_safe_create(self, user, validated_data, *args, **kwargs):
      if user.is_anonymous:
         return False

      return BookletContributor\
         .objects\
         .filter(
            user=user,
            booklet__urlid=validated_data['booklet']['urlid'],
            role__in=(BookletContributor.ROLE_MODERATOR, BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER)
         )\
         .count() > 0

class BookletTagViewset(LDPViewSet):
   def get_queryset(self, *args, **kwargs):
      related_booklet= get_booklet_user_pk(self.request.user, self.kwargs['pk'])
      return BookletTag.objects.filter(booklet=related_booklet)