#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_resource.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature HTTP Resource Test Cases
'''

import unittest
from unittest.mock import patch
from datature.http.resource import RESTResource


class TestResource(unittest.TestCase):
    """Datature HTTP Resource Test Cases."""

    @patch("datature.http.resource.Requester")
    def test_request(self, patch_requester):
        """Test resource request."""

        RESTResource.request("GET", "/test_end_point")

        patch_requester().request.assert_called_once_with(
            "GET", "/test_end_point", None, None, None, None)
