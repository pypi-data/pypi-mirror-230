import time
from typing import Any, Optional
from urllib.error import HTTPError

import requests

from asklora.brokerage.common import URL
from asklora.brokerage.exceptions import RetryException
from asklora.logger import logger


class BaseRestClient:
    def __init__(
        self,
        base_url: str,
        retry_max_count: int = 3,
        retry_wait_time: int = 3,
        retry_status_codes: list[int] | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("Need to set base URL")

        self.__session = requests.Session()

        self.base_url = base_url
        self.retry_max_count = retry_max_count
        self.retry_wait_time = retry_wait_time

        self.retry_status_codes = [429]
        if retry_status_codes:
            self.retry_status_codes.extend(retry_status_codes)

    def __request(
        self,
        method,
        path,
        data=None,
        base_url=None,
        raw_response: Optional[bool] = None,
    ):
        # Base URL settings
        base_url: str = base_url or self.base_url
        url = base_url + path

        # Extra arguments for requests module
        extra_args = {"allow_redirects": False}
        if method.upper() in ["GET", "DELETE"]:
            extra_args["params"] = data
        else:
            extra_args["json"] = data

        # Retry logic
        if self.retry_max_count < 0:
            self.retry_max_count = 0
        while self.retry_max_count >= 0:
            try:
                response = self.__make_request(
                    method=method,
                    url=url,
                    retry_count=self.retry_max_count,
                    extra_args=extra_args,
                )

                if not response.text or response.text == "":
                    return None

                return response.text if raw_response else response.json()

            except RetryException:
                logger.warning(
                    f"Waiting for {self.retry_wait_time} seconds before retrying to call {url} "
                    f"for {self.retry_max_count} more time(s)..."
                )
                time.sleep(self.retry_wait_time)
                self.retry_max_count -= 1
                continue

    def __make_request(self, method: str, url: URL, retry_count: int, extra_args: dict):
        """
        Perform one request, possibly raising RetryException in the case
        the response is 429. Otherwise, if error text contain "code" string,
        then it decodes to json object and returns APIError.
        Returns the body json in the 200 status.
        """

        response = self.__session.request(method, url, **extra_args)

        logger.info(f"{method} {url} [{response.status_code}]")
        logger.debug(
            {
                "method": method,
                "url": response.request.url,
                "status": response.status_code,
                "header": response.request.headers,
                "body": response.request.body,
            }
        )

        try:
            response.raise_for_status()

            return response
        except HTTPError:
            if response.status_code in self.retry_status_codes and retry_count > 0:
                # Retry the request if needed
                raise RetryException()
            else:
                # or re-raise it
                raise

    def get(self, path: str, data: Any = None, raw_response: Optional[bool] = None):
        return self.__request("GET", path, data, raw_response=raw_response)

    def post(self, path: str, data: Any = None, raw_response: Optional[bool] = None):
        return self.__request("POST", path, data, raw_response=raw_response)

    def put(self, path: str, data: Any = None, raw_response: Optional[bool] = None):
        return self.__request("PUT", path, data, raw_response=raw_response)

    def patch(self, path: str, data: Any = None, raw_response: Optional[bool] = None):
        return self.__request("PATCH", path, data, raw_response=raw_response)

    def delete(self, path: str, data: Any = None, raw_response: Optional[bool] = None):
        return self.__request("DELETE", path, data, raw_response=raw_response)
