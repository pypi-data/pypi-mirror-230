#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_asset.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Asset API Test Cases
'''

import unittest
from unittest.mock import MagicMock, patch
from datature.rest.asset.asset import Asset
from datature.rest.asset.upload_session import UploadSession


# pylint: disable=W0613
class TestAsset(unittest.TestCase):
    """Datature Asset API Resource Test Cases."""

    def test_list(self):
        """Test retrieve a list of assets."""
        Asset.request = MagicMock()

        Asset.list()

        Asset.request.assert_called_once_with("GET", "/asset/list", query=None)

    def test_list_pagination(self):
        """Test retrieve retrieve a list of assets with pagination."""
        Asset.request = MagicMock()

        Asset.list({"page": "nextPage", "limit": 5})

        Asset.request.assert_called_once_with("GET",
                                              "/asset/list",
                                              query={
                                                  "page": "nextPage",
                                                  "limit": 5
                                              })

    def test_retrieve(self):
        """Test retrieve an Asset."""
        Asset.request = MagicMock()

        Asset.retrieve("asset_id")

        Asset.request.assert_called_once_with("GET", "/asset/asset_id")

    def test_modify(self):
        """Test update an asset."""
        Asset.request = MagicMock()

        Asset.modify("asset_id", {"status": "status"})

        Asset.request.assert_called_once_with(
            "PUT", "/asset/asset_id", request_body={"status": "status"})

    def test_modify_custom_metadata(self):
        """Test update an asset custom metadata."""
        Asset.request = MagicMock()

        Asset.modify("asset_id", {"custom_metadata": "s"})

        Asset.request.assert_called_once_with(
            "PUT", "/asset/asset_id", request_body={"customMetadata": "s"})

    def test_delete(self):
        """Test delete an asset."""
        Asset.request = MagicMock()

        Asset.delete("asset_id")

        Asset.request.assert_called_once_with("DELETE", "/asset/asset_id")

    @patch("datature.rest.asset.upload_session.datature")
    def test_upload_session(self, patch_datature):
        """Test create Asset."""
        upload_session = Asset.upload_session()
        assert isinstance(upload_session, UploadSession)

    def test_group(self):
        """Test retrieve assets statistic."""
        Asset.request = MagicMock()

        Asset.group()

        Asset.request.assert_called_once_with("GET",
                                              "/asset/group",
                                              query={'group': None})
