#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_error.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Error Test Cases
'''

import unittest
from datature.error import BadRequestError


class TestError(unittest.TestCase):
    """Datature Logger Test Cases."""

    def test_bad_request_error(self):
        """Test BadRequestError class."""

        bad_request_error = BadRequestError("Test BadRequestError")

        error_string = repr(bad_request_error)

        assert error_string == ("BadRequestError" +
                                "(message=Test BadRequestError, detail=None)")
