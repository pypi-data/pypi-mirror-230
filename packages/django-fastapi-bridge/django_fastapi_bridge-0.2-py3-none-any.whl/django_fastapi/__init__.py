import django
from a2wsgi import ASGIMiddleware
from django.core.exceptions import ImproperlyConfigured

from .registry import get_default_api


def get_asgi_application():
    django.setup(set_prefix=False)
    api = get_default_api()
    if not api:
        raise ImproperlyConfigured(
            "There is no default API. Make sure you have added "
            '"django_fastapi" to INSTALLED_APPS'
        )
    return api


def get_wsgi_application():
    return ASGIMiddleware(get_asgi_application())
