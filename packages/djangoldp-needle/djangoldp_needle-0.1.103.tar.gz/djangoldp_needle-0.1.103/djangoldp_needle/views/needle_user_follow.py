from djangoldp.views import LDPViewSet

from ..models import NeedleUserFollow


class NeedleUserFollowViewset(LDPViewSet):
    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_anonymous:
            return []

        user = self.request.user
        return NeedleUserFollow.objects.filter(follow_from=user)
