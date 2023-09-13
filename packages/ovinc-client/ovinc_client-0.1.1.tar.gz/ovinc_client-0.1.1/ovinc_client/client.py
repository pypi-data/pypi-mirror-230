import json
import os
from distutils.util import strtobool

import requests
from requests import HTTPError, Response

from ovinc_client.components import Notice
from ovinc_client.constants import (
    APP_AUTH_HEADER_KEY,
    APP_AUTH_ID_KEY,
    APP_AUTH_SECRET_KEY,
    OVINC_CLIENT_SIGNATURE,
    RequestMethodEnum,
    ResponseData,
)
from ovinc_client.logger import logger


class OVINCClient:
    """
    OVINC Union Api Client
    """

    def __init__(self, app_code: str, app_secret: str, union_api_url: str):
        self._app_code = app_code
        self._app_secret = app_secret
        self._union_api_url = union_api_url
        self.notice = Notice(self, self._union_api_url)

    def call_api(self, method: str, url: str, params: dict) -> ResponseData:
        """
        call union api
        """

        # init kwargs
        kwargs = {"headers": self._build_headers(), "verify": bool(strtobool(os.getenv("OVINC_API_VERIFY", "True")))}
        if method == RequestMethodEnum.GET.value:
            kwargs["params"] = params
        else:
            kwargs["json"] = params

        # request
        response = requests.request(method=method, url=url, **kwargs)

        # parse response
        return self._parse_response(response)

    def _build_headers(self) -> dict:
        """
        build request header
        """

        return {
            "User-Agent": OVINC_CLIENT_SIGNATURE,
            APP_AUTH_HEADER_KEY: json.dumps(
                {
                    APP_AUTH_ID_KEY: self._app_code,
                    APP_AUTH_SECRET_KEY: self._app_secret,
                }
            ),
        }

    @classmethod
    def _parse_response(cls, response: Response) -> ResponseData:
        """
        parse response to json
        """

        try:
            response.raise_for_status()
        except HTTPError as err:
            logger.error("[ResponseCheckFailed] %s", err)
            return ResponseData(result=False)

        try:
            data = response.json()
        except Exception as err:
            logger.error("[ResponseParseFailed] %s", err)
            return ResponseData(result=False)

        return ResponseData(result=True, data=data)
