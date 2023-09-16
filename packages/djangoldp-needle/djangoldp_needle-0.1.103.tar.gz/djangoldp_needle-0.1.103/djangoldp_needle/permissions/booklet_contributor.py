from django.core.exceptions import ObjectDoesNotExist

from . import NeedleCustomPermissions


class BookletContributorPermissions(NeedleCustomPermissions):
    def get_container_permissions(self, request, view, obj=None):
        return {'view', 'add'}

    def get_object_permissions(self, request, view, obj):
        from ..models import BookletContributor # Avoid circular dependencie errors

        if request.user.is_anonymous:
            return {}

        try:
            user_booklet_contributor = BookletContributor.objects.filter(user=request.user, booklet=obj.booklet).get()
        except ObjectDoesNotExist:
            return {}

        res = set('view')
        if user_booklet_contributor.role == obj.ROLE_OWNER:
            res.add('change')

        return res