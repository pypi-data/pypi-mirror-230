from django.conf import settings

def get_avatar_level(expected_level):
    avatars = getattr(settings, 'NEEDLE_AVATARS', {})
    for avatar in avatars:
        if 'level' in avatars[avatar] and avatars[avatar]['level'] == expected_level:
            return avatar
    return None