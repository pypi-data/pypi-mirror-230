def autodiscover(*modules):
    from django.utils.module_loading import autodiscover_modules

    from .registry import get_default_api

    autodiscover_modules(*modules)
    return get_default_api()
