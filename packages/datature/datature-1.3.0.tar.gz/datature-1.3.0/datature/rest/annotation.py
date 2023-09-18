#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   annotation.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Annotation API
'''

from datature.utils import utils
from datature.http.resource import RESTResource
from datature.rest.operation import Operation
from datature.rest.types import (AnnotationExportOptions, AnnotationFormat,
                                 AnnotationMetadata)


class Annotation(RESTResource):
    """Datature Annotation API Resource."""

    @classmethod
    def list(cls, asset_id: str) -> dict:
        """Lists all annotations of a specific asset.

        :param asset_id: The ID of the asset.
        :return: A list of dictionaries containing annotation metadata with the following structure:

                .. code-block:: json

                         [
                            {
                                "id": "annot_8188782f-a86b-4961-9e2a-697509085460",
                                "object": "annotation",
                                "bound_type": "rectangle",
                                "bound": [
                                    [
                                        0.596875,
                                        0.8354166666666667
                                    ],
                                    [
                                        0.596875,
                                        0.9020833333333333
                                    ],
                                    [
                                        0.6546875,
                                        0.9020833333333333
                                    ],
                                    [
                                        0.6546875,
                                        0.8354166666666667
                                    ]
                                ],
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "asset_id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                                "tag": "tagName1"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Annotation.list("asset_6aea3395-9a72-4bb5-9ee0-19248c903c56")
        """
        return cls.request("GET", f"/annotation/list/{asset_id}")

    @classmethod
    def create(cls, annotation: AnnotationMetadata) -> dict:
        """Creates an annotation.

        :param annotation: The metadata of the annotation.
        :return: A dictionary containing the annotation metadata with the following structure:

                .. code-block:: json

                         {
                            "id": "annot_8188782f-a86b-4961-9e2a-697509085460",
                            "object": "annotation",
                            "bound_type": "rectangle",
                            "bound": [
                                [
                                    0.596875,
                                    0.8354166666666667
                                ],
                                [
                                    0.596875,
                                    0.9020833333333333
                                ],
                                [
                                    0.6546875,
                                    0.9020833333333333
                                ],
                                [
                                    0.6546875,
                                    0.8354166666666667
                                ]
                            ],
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "asset_id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "tag": "tagName1"
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Annotation.create({
                            "bound_type": "rectangle",
                            "bound": [[0.425, 0.49382716049382713], [0.425, 0.6419753086419753],
                                    [0.6, 0.6419753086419753], [0.6, 0.49382716049382713]],
                            "asset_id":
                                "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "tag":
                                "tagName1"
                        })
        """
        return cls.request("POST",
                           "/annotation",
                           request_body={
                               "assetId": annotation.get("asset_id"),
                               "tag": annotation.get("tag"),
                               "boundType": annotation.get("bound_type"),
                               "bound": annotation.get("bound")
                           })

    @classmethod
    def retrieve(cls, annotation_id: str) -> dict:
        """Retrieves a specific annotation using the annotation ID.

        :param annotation_id: The ID of the annotation.
        :return: A dictionary containing the specific annotation metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "annot_8188782f-a86b-4961-9e2a-697509085460",
                            "object": "annotation",
                            "bound_type": "rectangle",
                            "bound": [
                                [
                                    0.596875,
                                    0.8354166666666667
                                ],
                                [
                                    0.596875,
                                    0.9020833333333333
                                ],
                                [
                                    0.6546875,
                                    0.9020833333333333
                                ],
                                [
                                    0.6546875,
                                    0.8354166666666667
                                ]
                            ],
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "asset_id": "asset_6aea3395-9a72-4bb5-9ee0-19248c903c56",
                            "tag": "tagName1"
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Annotation.retrieve("asset_6aea3395-9a72-4bb5-9ee0-19248c903c56")
        """
        return cls.request("GET", f"/annotation/{annotation_id}")

    @classmethod
    def delete(cls, annotation_id: str) -> dict:
        """Deletes a specific annotation from the project.

        :param annotation_id: The ID of the annotation.
        :return: A dictionary containing the deleted annotation ID and the deletion status with the following structure:

                .. code-block:: json

                        {
                            "id": "annot_8188782f-a86b-4961-9e2a-697509085460",
                            "deleted": true
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Annotation.delete("asset_6aea3395-9a72-4bb5-9ee0-19248c903c56")
        """
        return cls.request("DELETE", f"/annotation/{annotation_id}")

    @classmethod
    def export(cls,
               annotation_format: AnnotationFormat,
               export_options: AnnotationExportOptions,
               background=False) -> dict:
        """Exports all annotations from the project in a specific annotation format.

        :param annotation_format: The annotation format for bounding boxes or polygons as a string.
        :param export_options: A dictionary containing other export options.
        :param background: Signal to complete the annotation export process in the background. Defaults to False.
        :return: A dictionary containing the operation metadata of the annotation export with the following structure:

                .. code-block:: json

                        {
                            "id": "op_508fc5d1-e908-486d-9e7b-1dca99b80024",
                            "object": "operation",
                            "op_link": "users/api|affaf/proje-1dca99b80024",
                            "status": {
                                "overview": "Queued",
                                "message": "Operation queued",
                                "time_updated": 1676621361765,
                                "time_scheduled": 1676621361765,
                                "progress": {
                                    "unit": "whole operation",
                                    "with_status": {
                                        "queued": 1,
                                        "running": 0,
                                        "finished": 0,
                                        "cancelled": 0,
                                        "errored": 0
                                    }
                                }
                            }
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Annotation.export("csv_fourcorner", {
                            "split_ratio": 0.5,
                            "seed": 1337,
                            "normalized": True,
                            "shuffle": True
                        })
        """
        response = cls.request("POST",
                               "/annotation/export",
                               query={"format": annotation_format},
                               request_body={
                                   "options": {
                                       "splitRatio":
                                       export_options.get("split_ratio"),
                                       "seed":
                                       export_options.get("seed"),
                                       "normalized":
                                       export_options.get("normalized"),
                                       "shuffle":
                                       export_options.get("shuffle")
                                   }
                               })

        if background:
            return response

        op_link = response["op_link"]
        return Operation.loop_retrieve(op_link)

    @classmethod
    def retrieve_exported_file(cls, op_id: str) -> dict:
        """Retrieves the download link of the exported annotations.

        :param op_id: The operation ID of the annotation export.
        :return: A dictionary with the download metadata of the annotation export with the following structure:

                .. code-block:: json

                    {
                        "op_id": "op_cf8c538a-bcb5-49a9-82cf-fb0d13b49bb1",
                        "op_link": "users/afb0d13b49bb1",
                        "status": "Finished",
                        "download": {
                            "method": "GET",
                            "url": "https://storage.googleape7ab37588a6ce2f692351757f5967",
                            "expiry": 1665476385234
                        }
                    }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Annotation.retrieve_exported_file(
                            "op_cf8c538a-bcb5-49a9-82cf-fb0d13b49bb1")
        """
        return cls.request("GET", f"/annotation/export/{op_id}")

    @classmethod
    def upload(cls,
               annotation_format: AnnotationFormat,
               file_path: str,
               background=False) -> dict:
        """Uploads annotations to project.

        :param annotation_format: The annotation format for bounding boxes or polygons as a string.
        :param file_path: The file path or folder containing the annotation metadata to be uploaded. The file contents should match the annotation format specified.
        :param background: Signal to complete the annotation upload process in the background. Defaults to False.
        :return: A dictionary containing the operation metadata of the annotation upload with the following structure:

                .. code-block:: json

                        {
                            "id": "op_508fc5d1-e908-486d-9e7b-1dca99b80024",
                            "object": "operation",
                            "op_link": "users/api|affaf/proje-1dca99b80024",
                            "status": {
                                "overview": "Queued",
                                "message": "Operation queued",
                                "time_updated": 1676621361765,
                                "time_scheduled": 1676621361765,
                                "progress": {
                                    "unit": "whole operation",
                                    "with_status": {
                                        "queued": 1,
                                        "running": 0,
                                        "finished": 0,
                                        "cancelled": 0,
                                        "errored": 0
                                    }
                                }
                            }
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Annotation.upload("csv_fourcorner",
                                                "Your file path")
        """
        upload_paths = utils.find_all_annotations_files(
            file_path, annotation_format)

        upload_list = []
        for upload_path in upload_paths:
            with open(upload_path, "rb") as file:
                upload_list.append(('files', (file.name, file.read(),
                                              'application/octet-stream')))

        response = cls.request(
            "POST",
            "/annotation/import",
            query={"format": annotation_format},
            request_files=upload_list,
        )

        if background:
            return response

        op_link = response["op_link"]
        return Operation.loop_retrieve(op_link)
