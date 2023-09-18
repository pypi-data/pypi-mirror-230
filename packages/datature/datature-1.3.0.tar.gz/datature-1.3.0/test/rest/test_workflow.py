#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_workflow.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Workflow API Test Cases
'''

import unittest
from unittest.mock import MagicMock
from datature.rest.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    """Datature Workflow API Resource Test Cases."""

    def test_list(self):
        """Test list all workflows."""
        Workflow.request = MagicMock()

        Workflow.list()

        Workflow.request.assert_called_once_with("GET", "/workflow/list")

    def test_retrieve(self):
        """Test retrieve a workflow."""
        Workflow.request = MagicMock()

        Workflow.retrieve("flow_id")

        Workflow.request.assert_called_once_with("GET", "/workflow/flow_id")

    def test_modify(self):
        """Test update a workflow."""
        Workflow.request = MagicMock()

        Workflow.modify("flow_id", {"title": "New Workflow Title"})

        Workflow.request.assert_called_once_with(
            "PUT",
            "/workflow/flow_id",
            request_body={"title": "New Workflow Title"})

    def test_delete(self):
        """Test delete a workflow."""
        Workflow.request = MagicMock()

        Workflow.delete("flow_id")

        Workflow.request.assert_called_once_with("DELETE", "/workflow/flow_id")
