from fastapi import FastAPI


class APIAlreadyRegistered(Exception):
    pass


class DefaultAPIAlreadyRegistered(APIAlreadyRegistered):
    pass


DEFAULT_API_NAME = "__default__"

_API = {}


def get_default_api() -> FastAPI:
    return _API.get(DEFAULT_API_NAME)


def set_default_api(api: FastAPI) -> None:
    if DEFAULT_API_NAME in _API:
        raise DefaultAPIAlreadyRegistered()
    _API[DEFAULT_API_NAME] = api
