#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_asset_upload_session.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Asset Upload Session API Test Cases
'''

import unittest
from unittest.mock import MagicMock, patch
from test.fixture.data import upload_session_fixture

from datature.error import Error
from datature.rest.asset.upload_session import UploadSession


# pylint: disable=W0613,R0913,C0103,W0703
class TestAssetUploadSession(unittest.TestCase):
    """Datature Asset Upload Session API Resource Test Cases."""

    @patch("datature.rest.asset.upload_session.datature")
    def test_add_with_file_not_exist(self, patch_datature):
        """Test add asset to upload with ."""
        patch_datature.ASSET_UPLOAD_BATCH_SIZE = 100

        upload_session = UploadSession()
        try:
            upload_session.add("assetPath")
        except Exception as exception:
            assert isinstance(exception, Error)

    @patch("datature.rest.asset.upload_session.filetype")
    @patch("datature.rest.asset.upload_session.struct")
    @patch("datature.rest.asset.upload_session.google_crc32c")
    @patch("datature.rest.asset.upload_session.path")
    @patch("datature.rest.asset.upload_session.open")
    @patch("datature.rest.asset.upload_session.datature")
    def test_add_with_duplicated_file(self, patch_datature, patch_open,
                                      patch_path, google_crc32c, struct,
                                      filetype):
        """Test add asset to upload with duplicated file."""
        patch_datature.ASSET_UPLOAD_BATCH_SIZE = 100

        upload_session = UploadSession()
        upload_session.file_name_map = {"assetName": {"path": "file_path"}}

        struct.unpack.return_value = [-384617082]
        patch_path.basename.return_value = "assetName"
        patch_path.getsize.return_value = 5613

        mock_guess = MagicMock()
        mock_guess.mime = "image/jpeg"
        filetype.guess.return_value = mock_guess

        try:
            upload_session.add("assetPath")
        except Exception as exception:
            assert isinstance(exception, Error)

    @patch("datature.rest.asset.upload_session.filetype")
    @patch("datature.rest.asset.upload_session.path")
    @patch("datature.rest.asset.upload_session.struct")
    @patch("datature.rest.asset.upload_session.google_crc32c")
    @patch("datature.rest.asset.upload_session.open")
    @patch("datature.rest.asset.upload_session.datature")
    def test_add_with_file_not_supported(self, patch_datature, patch_open,
                                         google_crc32c, struct, path,
                                         filetype):
        """Test add asset to upload with file not supported."""
        patch_datature.ASSET_UPLOAD_BATCH_SIZE = 100

        upload_session = UploadSession()

        struct.unpack.return_value = [-384617082]
        path.basename.return_value = "assetName"
        path.getsize.return_value = 5613

        mock_guess = MagicMock()
        mock_guess.mime = ""
        filetype.guess.return_value = mock_guess

        try:
            upload_session.add("assetPath")
        except Exception as exception:
            assert isinstance(exception, Error)

    @patch("datature.rest.asset.upload_session.filetype")
    @patch("datature.rest.asset.upload_session.path")
    @patch("datature.rest.asset.upload_session.struct")
    @patch("datature.rest.asset.upload_session.google_crc32c")
    @patch("datature.rest.asset.upload_session.open")
    @patch("datature.rest.asset.upload_session.datature")
    def test_add_with_file(self, patch_datature, patch_open, google_crc32c,
                           struct, path, filetype):
        """Test add asset to upload with file."""
        upload_session = UploadSession()

        patch_datature.ASSET_UPLOAD_BATCH_SIZE = 100
        struct.unpack.return_value = [-384617082]
        path.basename.return_value = "assetName"
        path.getsize.return_value = 5613

        mock_guess = MagicMock()
        mock_guess.mime = "image/jpeg"
        filetype.guess.return_value = mock_guess

        upload_session.add("assetPath")

    @patch("datature.rest.asset.upload_session.datature")
    def test_start_with_empty_assets(self, patch_datature):
        """Test start upload with empty assets ."""
        upload_session = UploadSession()

        try:
            upload_session.start(["main"])
        except Exception as exception:
            assert isinstance(exception, Error)

    @patch("datature.rest.asset.upload_session.request")
    @patch("datature.rest.asset.upload_session.open")
    @patch("datature.rest.asset.upload_session.datature")
    def test_start(self, patch_datature, patch_open, patch_request):
        """Test start upload with empty assets ."""
        patch_datature.ASSET_UPLOAD_BATCH_SIZE = 100

        upload_session = UploadSession()
        upload_session.assets = [{
            "filename": "test.jpeg",
            "mime": "image/jpeg",
            "size": 5613,
            "crc32c": -384617082
        }]
        upload_session.file_name_map = {"test.jpeg": {"path": "file_path"}}
        upload_session.request = MagicMock()

        upload_session.request.return_value = upload_session_fixture.upload_assets_response

        upload_session.assets = [{
            "filename": "test.jpeg",
            "mime": "image/jpeg",
            "size": 5613,
            "crc32c": -384617082
        }]

        upload_session.start(["main"], background=True)

    @patch("datature.rest.asset.upload_session.Operation")
    @patch("datature.rest.asset.upload_session.request")
    @patch("datature.rest.asset.upload_session.open")
    @patch("datature.rest.asset.upload_session.datature")
    def test_start_with_background(self, patch_datature, patch_open,
                                   patch_request, operation):
        """Test start upload with wait server process."""
        patch_datature.SHOW_PROGRESS = False
        upload_session = UploadSession()
        upload_session.assets = [{
            "filename": "test.jpeg",
            "mime": "image/jpeg",
            "size": 5613,
            "crc32c": -384617082
        }]
        upload_session.file_name_map = {"test.jpeg": {"path": "file_path"}}
        upload_session.request = MagicMock()

        upload_session.request.return_value = upload_session_fixture.upload_assets_response

        upload_session.assets = [{
            "filename": "test.jpeg",
            "mime": "image/jpeg",
            "size": 5613,
            "crc32c": -384617082
        }]

        upload_session.start(["main"])

        operation.loop_retrieve.assert_called()
