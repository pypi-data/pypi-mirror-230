from . import NeedleCustomPermissions


class BookletPermissions(NeedleCustomPermissions):
    def get_container_permissions(self, request, view, obj=None):
        perms = super().get_container_permissions(request, view, obj)
        perms.add('view')
        perms.add('add')
        return perms


    def get_object_permissions(self, request, view, obj):
        if request.user.is_anonymous:
            perms = set()
            if obj.accessibility_public:
                perms.add('view')
            return perms

        perms = super().get_object_permissions(request, view, obj)
        if obj.accessibility_public:
            perms.add('view')
        if obj.collaboration_allowed:
            perms.add('change')  # Per field permission check managed by validate method from BookletSerializer

        for contributor in obj.contributors.all():
            if contributor.user == request.user:
                perms.add('change') # Per field permission check managed by validate method from BookletSerializer
                if contributor.role == contributor.ROLE_OWNER:
                    perms.add('delete')
        return perms