import logging

import httpx

from .exceptions.status_exception import StatusException

logger = logging.getLogger(__name__)


def http_request(func):
    def wrap(self, url, include_token=True, **kwargs):
        logger.info(f"{str(func.__name__).split(':')[-1]} {url}")
        try:
            url = f"{self.url}{url}"
            if include_token:
                if self.token is None:
                    raise Exception("Client is not Authenticated")
                kwargs["headers"] = kwargs.get("headers", {})
                kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
            response = func(self, url, **kwargs)
            if response.status_code != 200:
                raise StatusException.from_response(response)
        except Exception as e:
            logger.error(f"{func.__name__} {url} {e}")
            raise e
        return response

    return wrap

class BaseClient:

    def __init__(self, url, token=None):
        self.url = url
        self.token = token
        try:
            response = self.get(f"", include_token=False)
            if response.status_code != 200:
                raise Exception(response.status_code)
        except Exception as e:
            raise Exception(f"could not connect to {url}: {e}")

    @http_request
    def get(self, url, **kwargs):
        return httpx.get(url, **kwargs)

    @http_request
    def post(self, url, **kwargs):
        return httpx.post(url, **kwargs)

    @http_request
    def delete(self, url, **kwargs):
        return httpx.delete(url, **kwargs)

