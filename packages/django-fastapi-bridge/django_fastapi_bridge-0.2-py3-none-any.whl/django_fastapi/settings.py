from django.conf import settings

AUTODISCOVER = getattr(settings, "FASTAPI_AUTODISCOVER", True)
AUTODISCOVER_MODULES = getattr(
    settings, "FASTAPI_AUTODISCOVER_MODULES", ["api"])

TITLE = getattr(settings, "FASTAPI_TITLE", "Django FastAPI")
VERSION = getattr(settings, "FASTAPI_VERSION", "unknown")
ROOT_PATH = getattr(settings, "FASTAPI_ROOT_PATH", "")
CORS_ENABLED = getattr(settings, "FASTAPI_CORS_ENABLED", False)
CORS_ALLOW_ORIGINS = getattr(settings, "FASTAPI_CORS_ALLOW_ORIGINS", ["*"])
CORS_ALLOW_CREDENTIALS = getattr(
    settings, "FASTAPI_CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOW_METHODS = getattr(settings, "FASTAPI_CORS_ALLOW_METHODS", ["*"])
CORS_ALLOW_HEADERS = getattr(settings, "FASTAPI_CORS_ALLOW_HEADERS", ["*"])
