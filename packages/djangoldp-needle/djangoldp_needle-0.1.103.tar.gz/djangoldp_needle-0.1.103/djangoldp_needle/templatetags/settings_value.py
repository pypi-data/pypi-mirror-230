from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def settings_value(name):
    if name == "INSTANCE_DEFAULT_CLIENT" :
        return getattr(settings, name, "")
    return ""
