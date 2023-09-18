#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_operation.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Operation API Test Cases
'''

import unittest
from unittest.mock import MagicMock
from test.fixture.data import operation_fixture
from datature.rest.operation import Operation
from datature.error import Error
import datature


class TestOperation(unittest.TestCase):
    """Datature Operation API Resource Test Cases."""

    def test_retrieve(self):
        """Test retrieve an operation."""
        Operation.request = MagicMock()

        Operation.retrieve("op_link")

        Operation.request.assert_called_once_with("GET",
                                                  "/operation",
                                                  query={"opLink": "op_link"})

    def test_loop_retrieve(self):
        """Test looping an operation."""
        datature.OPERATION_LOOPING_DELAY_SECONDS = 0
        Operation.request = MagicMock()

        Operation.request.side_effect = [
            operation_fixture.pending_operation_response,
            operation_fixture.finished_operation_response
        ]

        Operation.loop_retrieve("op_link")

    def test_loop_retrieve_with_status_error(self):
        """Test looping an operation with error."""
        datature.OPERATION_LOOPING_DELAY_SECONDS = 0
        Operation.request = MagicMock()

        Operation.request.side_effect = [
            operation_fixture.errored_operation_response
        ]

        try:
            Operation.loop_retrieve("op_link")
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, Error)

    def test_loop_retrieve_with_no_result_after_looping(self):
        """Test looping an operation with error."""
        datature.OPERATION_LOOPING_DELAY_SECONDS = 0
        Operation.request = MagicMock()

        Operation.request.side_effect = [
            operation_fixture.pending_operation_response,
            operation_fixture.pending_operation_response
        ]

        assert Operation.loop_retrieve("op_link", 2) is None
