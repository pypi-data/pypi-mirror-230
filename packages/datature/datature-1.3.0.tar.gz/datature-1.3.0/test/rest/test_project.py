#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_project.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Project API Test Cases
'''

import unittest
from unittest.mock import MagicMock
from datature.rest.project import Project


class TestProject(unittest.TestCase):
    """Datature Project API Resource Test Cases."""

    def test_retrieve(self):
        """Test retrieve a project."""
        Project.request = MagicMock()

        Project.retrieve()

        Project.request.assert_called_once_with("GET", "/project")

    def test_modify(self):
        """Test update a project."""
        Project.request = MagicMock()

        Project.modify({"name": "New Project Name"})

        Project.request.assert_called_once_with(
            "PUT", "/project", request_body={"name": "New Project Name"})

    def test_quota(self):
        """Test retrieve project quota."""
        Project.request = MagicMock()

        Project.quota()

        Project.request.assert_called_once_with("GET", "/project/quota")

    def test_insight(self):
        """Test retrieve a project insight."""
        Project.request = MagicMock()

        Project.insight()

        Project.request.assert_called_once_with("GET", "/project/insight")

    def test_users(self):
        """Test retrieve project users."""
        Project.request = MagicMock()

        Project.users()

        Project.request.assert_called_once_with("GET", "/project/users")
