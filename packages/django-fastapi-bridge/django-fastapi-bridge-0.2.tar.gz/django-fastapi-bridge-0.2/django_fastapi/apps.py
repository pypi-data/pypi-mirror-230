from django.apps import AppConfig
from fastapi import FastAPI


class FastapiBridgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_fastapi"

    def ready(self):
        from . import settings
        from .registry import set_default_api
        from .utils import autodiscover

        api = FastAPI(
            title=settings.TITLE,
            version=settings.VERSION,
            root_path=settings.ROOT_PATH,
        )
        set_default_api(api)

        if settings.CORS_ENABLED:
            from fastapi.middleware.cors import CORSMiddleware

            api.add_middleware(
                CORSMiddleware,
                allow_origins=settings.CORS_ALLOW_ORIGINS,
                allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
                allow_methods=settings.CORS_ALLOW_METHODS,
                allow_headers=settings.CORS_ALLOW_HEADERS,
            )

        if settings.AUTODISCOVER:
            modules = list(settings.AUTODISCOVER_MODULES)
            autodiscover(*modules)
