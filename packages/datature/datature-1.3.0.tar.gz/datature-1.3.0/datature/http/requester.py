#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   requester.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   A wrapper to make HTTP requests
'''

import os
import json
import platform
from urllib.parse import urlencode

import humps
from requests import Response, request

import datature
from datature import error, logger

system = platform.system()
machine = platform.machine()
python_version = platform.python_version()

# pylint: disable=R0913,R0903
class Requester():
    """An HTTP requester."""

    def request(self,
                method,
                url,
                query=None,
                request_body=None,
                request_headers=None,
                request_files=None):
        """Create an HTTP requester.

        :param method: The request method: ["get", "post", "put", "delete"]
        :param url: The request url
        :param query: The query object
        :param request_body: The request body
        :param request_headers: If have custom request headers
        :param request_files: If have file to upload
        """

        # CHeck Secret
        if datature.secret_key is None:
            raise error.UnauthorizedError(
                "No project secret key provided. (Set your secret key"
                " using datature.secret_key = <secret_key>)")

        if 'DATATURE_API_BASE_URL' in os.environ:
            datature.API_BASE_URL = os.environ['DATATURE_API_BASE_URL']

        absolute_url = f"{datature.API_BASE_URL}{url}"

        # Assemble queries and request body.
        post_data = None
        post_files = None

        if query:
            encoded_params = urlencode(query or {})
            absolute_url = f'{absolute_url}?{encoded_params}'

        if request_body:
            post_data = json.dumps(request_body)

        # Assemble request headers
        headers = self._make_headers(method, request_headers)

        # Open files in binary mode.
        # Requests may attempt to provide the Content-Length header for us,
        if request_files:
            post_files = request_files
            # Remove Content-Type
            headers.pop("Content-Type")

        logger.log_info("API request:", method=method, path=absolute_url)
        logger.log_debug("API request body:", post_data=post_data)

        # Call request to do a real HTTP call, default timeout 120s
        response = request(method,
                           absolute_url,
                           headers=headers,
                           data=post_data,
                           files=post_files,
                           timeout=datature.HTTP_TIMEOUT_SECONDS)

        self._interpret_response(response)

        logger.log_info("API response:",
                        path=absolute_url,
                        response_code=response.status_code)
        logger.log_debug("API response body:", body=response.json())

        snake_case_response = self._snake_case_response(response)

        return snake_case_response

    def _make_headers(self, method, request_headers):
        """Make request headers

        :param method: The request method
        :param request_headers: The custom request headers
        """
        headers = {
            "Secret-Key": datature.secret_key,
            "User-Agent": f"DatatureSDK/{datature.SDK_VERSION} " \
                          f"(Python/{python_version}; {system}/{machine})",
        }

        if method in ["POST", "PUT"]:
            headers["Content-Type"] = "application/json"

        if request_headers is not None:
            for key, value in request_headers.items():
                headers[key] = value

        return headers

    def _interpret_response(self, response: Response):
        """Check if need throw Error

        :param response: The request response
        """
        response_code = response.status_code
        response_data = response.json()
        if not 200 <= response_code < 300:
            error_message = response_data["message"]

            logger.log_info(
                "API error received:",
                error_code=response.status_code,
                error_message=error_message,
            )

            if response_code == 403:
                raise error.ForbiddenError(error_message, response_data)
            if response_code == 404:
                raise error.NotFoundError(
                    error_message,
                    response_data,
                )
            if response_code == 429:
                raise error.TooManyRequestsError(error_message, response_data)

            raise error.InternalServerError("Internal Server Error",
                                            response_data)

    def _snake_case_response(self, response: Response):
        """Convert CamelCase response to snake_case

        :param response: The request response
        """
        return humps.decamelize(response.json())
