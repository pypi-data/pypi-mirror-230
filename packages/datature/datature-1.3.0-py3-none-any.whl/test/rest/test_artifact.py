#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_artifact.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Artifact API Test Cases
'''

import unittest
from unittest.mock import MagicMock
from datature.rest.artifact import Artifact


class TestArtifact(unittest.TestCase):
    """Datature Artifact API Resource Test Cases."""

    def test_list(self):
        """Test list all artifacts."""
        Artifact.request = MagicMock()

        Artifact.list()

        Artifact.request.assert_called_once_with("GET", "/artifact/list")

    def test_retrieve(self):
        """Test retrieve an artifact."""
        Artifact.request = MagicMock()

        Artifact.retrieve("artifact_id")

        Artifact.request.assert_called_once_with("GET",
                                                 "/artifact/artifact_id")

    def test_list_exported(self):
        """Test artifact exported models."""
        Artifact.request = MagicMock()

        Artifact.list_exported("artifact_id")

        Artifact.request.assert_called_once_with(
            "GET", "/artifact/artifact_id/models")

    def test_export_model(self):
        """Test export a artifact model."""
        Artifact.request = MagicMock()

        Artifact.export_model("artifact_id", "tensorflow")

        Artifact.request.assert_called_once_with(
            "POST",
            "/artifact/artifact_id/export",
            request_body={"format": "tensorflow"})
