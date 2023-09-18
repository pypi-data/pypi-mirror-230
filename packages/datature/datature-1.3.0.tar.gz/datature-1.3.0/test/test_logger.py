#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_logger.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Logger Test Cases
'''

import unittest
from unittest.mock import patch
from datature.logger import log_debug, log_info
import datature


class TestLogger(unittest.TestCase):
    """Datature Logger Test Cases."""

    @patch("datature.logger.logger")
    def test_log_debug(self, patch_logging):
        """Test log debug function."""

        datature.LOG_LEVEL = "debug"
        log_debug("log_debug test.")

        patch_logging.debug.assert_called_once_with("message=log_debug test.")

    @patch("datature.logger.logger")
    def test_log_info(self, patch_logging):
        """Test log info function."""

        datature.LOG_LEVEL = "info"
        log_info("log_info test.")

        patch_logging.info.assert_called_once_with("message=log_info test.")
