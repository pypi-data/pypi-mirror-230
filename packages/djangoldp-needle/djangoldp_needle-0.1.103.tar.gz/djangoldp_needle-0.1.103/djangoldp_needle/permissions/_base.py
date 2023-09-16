from djangoldp.permissions import LDPPermissions


class NeedleCustomPermissions(LDPPermissions):
    # Remove permissions check from guardian
    def get_all_user_object_permissions(self, user, obj):
        return set()