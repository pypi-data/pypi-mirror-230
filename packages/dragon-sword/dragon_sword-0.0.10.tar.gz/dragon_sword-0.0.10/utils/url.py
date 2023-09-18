from urllib.parse import urlencode


def url_last_name(url: str):
    return url.rsplit('/', 1)[1]


def dict_to_param(data: dict):
    return urlencode(data)
