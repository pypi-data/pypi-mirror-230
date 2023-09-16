from django.http import HttpResponse, JsonResponse
from django.conf import settings

def avatars_animals_list(request, *args, **kwargs):
    return JsonResponse(getattr(settings, 'NEEDLE_AVATARS', {}))

def avatars_quality_list(request, *args, **kwargs):
    return JsonResponse({'qualities': getattr(settings, 'NEEDLE_QUALITIES', {})})