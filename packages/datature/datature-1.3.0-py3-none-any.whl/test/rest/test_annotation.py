#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_annotation.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Annotation API Test Cases
'''

import unittest
from unittest.mock import MagicMock, patch
from test.fixture.mock import MockResponse
from test.fixture.data import operation_fixture
from datature.rest.annotation import Annotation
from datature.error import Error


class TestAnnotation(unittest.TestCase):
    """Datature Annotation API Resource Test Cases."""

    def test_list(self):
        """Test retrieve a list of annotations."""
        Annotation.request = MagicMock()

        Annotation.list("asset_id")

        Annotation.request.assert_called_once_with(
            "GET", "/annotation/list/asset_id")

    def test_create(self):
        """Test create an annotation."""
        Annotation.request = MagicMock()

        Annotation.create({
            "asset_id":
            "asset_id",
            "tag":
            "tagName",
            "bound_type":
            "bound_type",
            "bound": [[0.425, 0.49382716049382713],
                      [0.425, 0.6419753086419753], [0.6, 0.6419753086419753],
                      [0.6, 0.49382716049382713]]
        })

        Annotation.request.assert_called_once_with(
            "POST",
            "/annotation",
            request_body={
                "assetId":
                "asset_id",
                "tag":
                "tagName",
                "boundType":
                "bound_type",
                "bound": [[0.425, 0.49382716049382713],
                          [0.425,
                           0.6419753086419753], [0.6, 0.6419753086419753],
                          [0.6, 0.49382716049382713]]
            })

    def test_retrieve(self):
        """Test retrieve an annotation."""
        Annotation.request = MagicMock()

        Annotation.retrieve("annotation_id")

        Annotation.request.assert_called_once_with(
            "GET", "/annotation/annotation_id")

    def test_delete(self):
        """Test delete an annotation."""
        Annotation.request = MagicMock()

        Annotation.delete("annotation_id")

        Annotation.request.assert_called_once_with(
            "DELETE", "/annotation/annotation_id")

    def test_export_with_background(self):
        """Test export annotations."""
        Annotation.request = MagicMock()

        Annotation.export("csv_fourcorner",
                          export_options={
                              "split_ratio": 0.4,
                              "seed": 1337,
                          },
                          background=True)
        Annotation.request.assert_called_once_with(
            "POST",
            "/annotation/export",
            query={"format": "csv_fourcorner"},
            request_body={
                "options": {
                    "splitRatio": 0.4,
                    "seed": 1337,
                    "normalized": None,
                    "shuffle": None
                }
            })

    @patch("datature.rest.annotation.Operation")
    def test_export(self, operation):
        """Test export annotations."""
        Annotation.request = MagicMock()

        Annotation.export("csv_fourcorner",
                          export_options={
                              "split_ratio": 0.4,
                              "seed": 1337,
                          })
        Annotation.request.side_effect = MockResponse(
            operation_fixture.pending_operation_response, 200)

        operation.loop_retrieve.assert_called()

    def test_retrieve_exported_file(self):
        """Test get export annotations."""
        Annotation.request = MagicMock()

        Annotation.retrieve_exported_file("op_id")
        Annotation.request.assert_called_once_with("GET",
                                                   "/annotation/export/op_id")

    def test_upload_file_not_exist(self):
        """Test import annotation with file not exist."""

        Annotation.request = MagicMock()

        try:
            Annotation.upload("csv_fourcorner", "pathPath")
        # pylint: disable=W0703
        except Exception as exception:
            assert isinstance(exception, Error)

    @patch("datature.rest.annotation.Operation")
    @patch("datature.rest.annotation.utils")
    @patch("datature.rest.annotation.open")
    def test_upload_with_file(self, patch_open, patch_utils, operation):
        """Test import annotation with file exist."""

        Annotation.request = MagicMock()

        patch_utils.find_all_annotations_files.return_value = []
        patch_open = MagicMock()
        patch_open.side_effect = True

        Annotation.request.side_effect = [
            operation_fixture.pending_operation_response
        ]
        Annotation.upload("csv_fourcorner", "pathPath")

        operation.loop_retrieve.assert_called()

    @patch("datature.rest.annotation.utils")
    @patch("datature.rest.annotation.open")
    def test_upload_with_file_background(
        self,
        patch_open,
        patch_utils,
    ):
        """Test import annotation with file exist."""

        Annotation.request = MagicMock()

        patch_utils.find_all_annotations_files.return_value = []
        patch_open = MagicMock()
        patch_open.side_effect = True

        Annotation.request.side_effect = [
            operation_fixture.pending_operation_response
        ]
        assert Annotation.upload(
            "csv_fourcorner", "pathPath",
            background=True) == operation_fixture.pending_operation_response
