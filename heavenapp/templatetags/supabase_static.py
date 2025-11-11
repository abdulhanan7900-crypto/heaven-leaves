from django import template
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def supabase_static(path):
    """
    Returns the full URL to a static file in Supabase storage.
    Usage: {% supabase_static 'css/style.css' %}
    """
    supabase_url = os.environ.get('SUPABASE_URL')
    bucket_name = 'heavenleaves'
    
    if supabase_url:
        return f'{supabase_url}/storage/v1/object/public/{bucket_name}/static/{path}'
    else:
        # Fallback to local static files during development
        from django.templatetags.static import static
        return static(path)