from enum import Enum

import requests


class HTTPMethod(Enum):
    POST = "POST"
    GET = "GET"
    PATCH = "PATCH"
    DELETE = "DELETE"


def http_request(http_url, method, timeout=5, *args, **kwargs):
    session = requests.Session()
    res = session.request(method=method, url=http_url, timeout=timeout, *args, **kwargs)
    return res
