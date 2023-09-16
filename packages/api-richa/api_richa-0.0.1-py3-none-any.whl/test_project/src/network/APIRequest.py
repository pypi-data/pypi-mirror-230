import json
from enum import Enum
import requests
from requests import ConnectTimeout, HTTPError, Timeout
from dataclasses import dataclass


class StatusCodes(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502


@dataclass
class Response:
    code: int
    content: str


class APIRequest:
    REQUEST_TIMEOUT = 2

    def __init__(self, base_url):
        self.BASE_URL = base_url

    # Post call
    def postRequest(self, url_endpoint, payload, headers=None, auth=None, params=None):
        try:
            url = self.BASE_URL + url_endpoint
            response = requests.post(url=url, headers=headers, data=json.dumps(payload), timeout=self.REQUEST_TIMEOUT,
                                     auth=auth, params=params)
            response.raise_for_status()
        except (ConnectTimeout, HTTPError, Timeout, ConnectionError):
            pass
        return getResponse(response)

    # GET CALL
    def getRequest(self, url_endpoint, headers=None, params=None, auth=None):
        try:
            url = self.BASE_URL + url_endpoint
            response = requests.get(url=url, headers=headers, params=params,
                                    timeout=self.REQUEST_TIMEOUT, auth=auth)
            response.raise_for_status()
        except (ConnectTimeout, HTTPError, Timeout, ConnectionError):
            pass
        return getResponse(response)

    # PUT call : updates the entire resource .
    def putRequest(self, url_endpoint, payload=None, headers=None, auth=None):
        try:
            url = self.BASE_URL + url_endpoint
            response = requests.put(url=url, headers=headers, data=json.dumps(payload),
                                    timeout=self.REQUEST_TIMEOUT, auth=auth)
        except (ConnectTimeout, HTTPError, Timeout, ConnectionError):
            pass
        return getResponse(response)

    # Patch call
    def patchRequest(self, url_endpoint, payload=None, headers=None, auth=None):
        try:
            url = self.BASE_URL + url_endpoint
            response = requests.patch(url=url, headers=headers, data=json.dumps(payload),
                                      timeout=self.REQUEST_TIMEOUT, auth=auth)
        except (ConnectTimeout, HTTPError, Timeout, ConnectionError):
            pass
        return getResponse(response)

    # Delete call
    def deleteRequest(self, url_endpoint, headers=None, params=None, payload=None, auth=None):
        try:
            url = self.BASE_URL + url_endpoint
            response = requests.delete(url=url, headers=headers, data=json.dumps(payload),
                                       params=params, timeout=self.REQUEST_TIMEOUT, auth=auth)
        except (ConnectTimeout, HTTPError, Timeout, ConnectionError):
            pass
        return getResponse(response)


def getResponse(response) -> Response:
    try:
        code = response.status_code
        content = response.json()
    except Exception:
        content = response.text
        pass
    return Response(code, content)
