from django.core.exceptions import ValidationError
from django.http import Http404
from djangoldp.views import LDPViewSet

from ..models import Avatar


class AvatarViewset(LDPViewSet):
    def get_object(self):
        try:
            obj = Avatar.objects.filter(creator__slug=self.kwargs['slug']).get()
        except (TypeError, ValueError, ValidationError):
            raise Http404

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
