#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_requester.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature HTTP Resource Test Cases
'''

import unittest
from unittest.mock import patch
from test.fixture.mock import MockResponse
from test.fixture.data import error_fixture, operation_fixture
from datature.http.requester import Requester
from datature.error import (ForbiddenError, NotFoundError,
                            TooManyRequestsError, InternalServerError,
                            UnauthorizedError)
import datature


class TestRequester(unittest.TestCase):
    """Datature HTTP Resource Test Cases."""

    def test_request_with_no_project_key(self):
        """Test resource request."""

        datature.secret_key = None
        try:
            # pylint: disable=W0212
            Requester().request("GET", "test_end_poimt")
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, UnauthorizedError)

    @patch("datature.http.requester.request")
    def test_request_with_query(self, patch_request):
        """Test resource request."""

        datature.secret_key = "project_secret"

        patch_request.return_value = MockResponse(
            operation_fixture.pending_operation_response, 200)

        # pylint: disable=W0212
        response = Requester().request("GET",
                                       "test_end_poimt",
                                       query={"limit": 5},
                                       request_body={"key": "value"})
        assert response == operation_fixture.pending_operation_response

    @patch("datature.http.requester.request")
    def test_request_with_request_files(self, patch_request):
        """Test resource request with request files."""

        datature.secret_key = "project_secret"

        patch_request.return_value = MockResponse(
            operation_fixture.pending_operation_response, 200)

        # pylint: disable=W0212
        response = Requester().request("POST",
                                       "test_end_poimt",
                                       request_files="FileObject")
        assert response == operation_fixture.pending_operation_response

    def test_make_headers_with_get_method(self):
        """Test make headers."""

        datature.secret_key = "project_secret"
        # pylint: disable=W0212
        headers = Requester()._make_headers("GET", {})

        assert headers["Secret-Key"] == "project_secret"

    def test_make_headers_with_post_method(self):
        """Test make headers with post method."""

        datature.secret_key = "project_secret"
        # pylint: disable=W0212
        headers = Requester()._make_headers("POST", {})

        assert headers["Secret-Key"] == "project_secret"
        assert headers["Content-Type"] == "application/json"

    def test_make_headers_with_supplied_headers(self):
        """Test make headers with supplied headers."""

        datature.secret_key = "project_secret"
        # pylint: disable=W0212
        headers = Requester()._make_headers("GET", {
            "Connection": "keep-alive",
            "Accept": "*/*"
        })

        assert headers["Secret-Key"] == "project_secret"
        assert headers["Accept"] == "*/*"

    def test_interpret_response_with_403(self):
        """Test interpret response with 403 code."""

        try:
            # pylint: disable=W0212
            Requester()._interpret_response(
                MockResponse(error_fixture.forbidden_error_response, 403))
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, ForbiddenError)

    def test_interpret_response_with_404(self):
        """Test interpret response with 404 code."""

        try:
            # pylint: disable=W0212
            Requester()._interpret_response(
                MockResponse(error_fixture.not_found_error_response, 404))
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, NotFoundError)

    def test_interpret_response_with_429(self):
        """Test interpret response with 429 code."""

        try:
            # pylint: disable=W0212
            Requester()._interpret_response(
                MockResponse(error_fixture.too_many_requests_error_response,
                             429))
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, TooManyRequestsError)

    def test_interpret_response_with_500(self):
        """Test interpret response with 500 code."""

        try:
            # pylint: disable=W0212
            Requester()._interpret_response(
                MockResponse(error_fixture.internal_server_error_response,
                             500))
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, InternalServerError)
