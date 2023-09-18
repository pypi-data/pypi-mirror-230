#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   asset.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Asset API
'''

from datature.http.resource import RESTResource
from datature.rest.asset.upload_session import UploadSession
from datature.rest.types import AssetMetadata, Pagination


class Asset(RESTResource):
    """Datature Annotation API Resource."""

    @classmethod
    def list(cls, pagination: Pagination = None) -> dict:
        """Retrieves a list of all assets in the project.

        :param pagination: A dictionary containing the limit of the number of assets to be returned in each page (defaults to 10), and the page cursor for page selection (defaults to the first page).
        :return: A dictionary of asset metadata with the following structure:

                .. code-block:: json

                        {
                            "prev_page": "YjYzYmJkM2FjN2UxOTA4ZmU0ZjE0Yjk5Mg",
                            "next_page": "ZjYzYmJkM2FjN2UxOTA4ZmU0ZjE0YjlhMw",
                            "data": [
                                {
                                    "id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                                    "object": "asset",
                                    "filename": "17.jpg",
                                    "project": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                    "create_date": 1673253803928,
                                    "metadata": {
                                        "file_size": 21185,
                                        "mime_type": "image/jpeg",
                                        "status": "annotated",
                                        "height": 480,
                                        "width": 640
                                    },
                                    "statistic": {
                                        "tags_count": [
                                            {
                                                "name": "tagName1",
                                                "count": 1
                                            },
                                            {
                                                "name": "tagName2",
                                                "count": 16
                                            }
                                        ],
                                        "annotation_total": 18
                                    },
                                    "url": "https://s.googleapis.com/assets.datature.io/c09fd3a6d04"
                                }
                            ]
                        }
        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Asset.list({
                            "limit": 2,
                            "page": "ZjYzYmJkM2FjN2UxOTA4ZmU0ZjE0Yjk5Mg"
                        }))

        """
        return cls.request("GET", "/asset/list", query=pagination)

    @classmethod
    def retrieve(cls, asset_id_or_name: str) -> dict:
        """Retrieves a specific asset using the asset ID or file name.

        :param asset_id_or_name: The ID or file name of the asset as a string.
        :return: A dictionary containing the metadata of one asset with the following structure:

                .. code-block:: json

                        {
                            "id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "object": "asset",
                            "filename": "17.jpg",
                            "project": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "create_date": 1673253803928,
                            "metadata": {
                                "file_size": 21185,
                                "mime_type": "image/jpeg",
                                "status": "annotated",
                                "height": 480,
                                "width": 640
                            },
                            "statistic": {
                                "tags_count": [
                                    {
                                        "name": "tagName1",
                                        "count": 1
                                    },
                                    {
                                        "name": "tagName2",
                                        "count": 16
                                    }
                                ],
                                "annotation_total": 17
                            },
                            "url": "https://s.googleapis.com/assets.datature.io/c09fd3a6d04"
                        }
        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Asset.retrieve("asset_6aea3395-9a72-4bb5-9ee0-19248c903c56")
        """
        return cls.request("GET", f"/asset/{asset_id_or_name}")

    @classmethod
    def modify(cls, asset_id_or_name: str, asset_meta: AssetMetadata) -> dict:
        """Updates the metadata of a specific asset.

        :param asset_id_or_name: The ID or file name of the asset as a string.
        :param asset_meta: The new metadata of the asset to be updated.
        :return: A dictionary of the updated asset metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "object": "asset",
                            "filename": "17.jpg",
                            "project": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "create_date": 1673253803928,
                            "metadata": {
                                "file_size": 21185,
                                "mime_type": "image/jpeg",
                                "status": "annotated",
                                "height": 480,
                                "width": 640
                            },
                            "statistic": {
                                "tags_count": [
                                    {
                                        "name": "tagName1",
                                        "count": 1
                                    },
                                    {
                                        "name": "tagName2",
                                        "count": 16
                                    }
                                ],
                                "annotation_total": 17
                            },
                            "url": "https://s.googleapis.com/assets.datature.io/c09fd3a6d04"
                        }
        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Asset.modify(
                            "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            {
                                "status": "annotated"
                            }
                        )
        """
        request_body = {}
        if asset_meta.get("status") is not None:
            request_body["status"] = asset_meta.get("status")

        if asset_meta.get("custom_metadata") is not None:
            request_body["customMetadata"] = asset_meta.get("custom_metadata")

        return cls.request("PUT",
                           f"/asset/{asset_id_or_name}",
                           request_body=request_body)

    @classmethod
    def delete(cls, asset_id_or_name: str) -> dict:
        """Deletes a specific asset from the project.

        :param asset_id_or_name: The ID or file name of the asset as a string.
        :return: A dictionary containing the deleted asset ID and the deletion status with the following structure.

                .. code-block:: json

                        {
                            "id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "deleted": true
                        }
        :example:

                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Asset.delete(
                            "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                        )
        """
        return cls.request("DELETE", f"/asset/{asset_id_or_name}")

    @classmethod
    def upload_session(cls) -> dict:
        """
        Creates an upload session to upload or update assets. For bulk asset upload, we allow the user to add up to 5000 assets in one single upload session.

        To add an asset into the upload session, simply include its file path as an argument when calling the add function. Once all assets have been added, you can initiate the upload process by calling the start function.

        :return: UploadSession class
        :example:

                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        files = os.listdir("Your assets folder")

                        batch_size = 5000
                        num_batches = len(files) // batch_size

                        # split to batches, each batch includes 5000 assets
                        batches = [files[i*batch_size:
                                    (i+1) * batch_size] for i in range(num_batches)]

                        if len(files) % batch_size != 0:
                            batches.append(files[num_batches * batch_size:])

                        # upload batches
                        for i, batch in enumerate(batches):

                            upload_session = datature.Asset.upload_session()

                            for file in batch:
                                upload_session.add(f"{Your assets folder}/{file}")

                            upload_session.start(["main"],)
        """
        return UploadSession()

    @classmethod
    def group(cls, group: str = None) -> dict:
        """Retrieve asset statistics categorized by asset group and asset status.

        :param group: A comma-separated string of name(s) of asset group(s).
        :return: A list of dictionaries of the categorized asset statistics with the following structure:

                .. code-block:: json

                        [
                            {
                                "cohort": "main",
                                "statistic": {
                                    "assetTotal": 446,
                                    "assetAnnotated": 13,
                                    "assetReviewed": 0,
                                    "assetTofixed": 0,
                                    "assetCompleted": 0
                                }
                            }
                        ]
        :example:

                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Asset.group()
        """
        return cls.request("GET", "/asset/group", query={"group": group})
