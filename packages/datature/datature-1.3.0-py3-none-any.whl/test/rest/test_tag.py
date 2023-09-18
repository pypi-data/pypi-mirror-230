#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_tag.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Project API Test Cases.
'''

import unittest
from unittest.mock import MagicMock
from datature.rest.tag import Tag


class TestTag(unittest.TestCase):
    """Datature Tag API Resource Test Cases."""

    def test_list(self):
        """Test list tags."""
        Tag.request = MagicMock()

        Tag.list()

        Tag.request.assert_called_once_with("GET", "/tag/list")

    def test_create(self):
        """Test create a tag."""
        Tag.request = MagicMock()

        Tag.create("New Tag Name")

        Tag.request.assert_called_once_with(
            "POST", "/tag", request_body={"name": "New Tag Name"})

    def test_modify(self):
        """Test update a tag."""
        Tag.request = MagicMock()

        Tag.modify(1, "New Tag Name")

        Tag.request.assert_called_once_with(
            "PUT", "/tag/1", request_body={"name": "New Tag Name"})

    def test_delete(self):
        """Test delete a tag."""
        Tag.request = MagicMock()

        Tag.delete(1)

        Tag.request.assert_called_once_with("DELETE", "/tag/1")
