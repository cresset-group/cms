import jinja2
from django import template
from django_jinja import library

from cms.apps.pages.models import Page

register = template.Library()

@register.simple_tag
def get_preview_parameters(obj):
    if not isinstance(obj, Page):
        return 'preview=1'

    return f'preview=1&version={obj.version}'