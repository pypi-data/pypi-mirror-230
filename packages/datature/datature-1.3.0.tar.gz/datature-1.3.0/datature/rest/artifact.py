#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   artifact.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Artifact API
'''

from datature.http.resource import RESTResource


class Artifact(RESTResource):
    """Datature Artifact API Resource."""

    @classmethod
    def list(cls) -> dict:
        """Lists all artifacts in the project.

        :return: A list of dictionaries containing the artifact metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "id": "artifact_63bd140e67b42dc9f431ffe2",
                                "object": "artifact",
                                "is_training": false,
                                "step": 3000,
                                "flow_title": "Blood Cell Detector",
                                "run_id": "run_63bd08d8cdf700575fa4dd01",
                                "files": [
                                    {
                                        "name": "ckpt-13.data-00000-of-00001",
                                        "md5": "5a96886e53f98daae379787ee0f22bda"
                                    }
                                ],
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "artifact_name": "ckpt-13",
                                "create_date": 1673335822851,
                                "metric": {
                                    "total_loss": 0.548,
                                    "classification_loss": 0.511,
                                    "localization_loss": 0.006,
                                    "regularization_loss": 0.03
                                },
                                "is_deployed": false,
                                "exports": [],
                                "model_type": "efficientdet-d1-640x640"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Artifact.list()
        """
        return cls.request("GET", "/artifact/list")

    @classmethod
    def retrieve(cls, artifact_id: str) -> dict:
        """Retrieves a specific artifact using the artifact ID.

        :param artifact_id: The ID of the artifact as a string.
        :return: A dictionary containing the specific artifact metadata with the following structure:

                .. code-block:: json

                            {
                                "id": "artifact_63bd140e67b42dc9f431ffe2",
                                "object": "artifact",
                                "is_training": false,
                                "step": 3000,
                                "flow_title": "Blood Cell Detector",
                                "run_id": "run_63bd08d8cdf700575fa4dd01",
                                "files": [
                                    {
                                        "name": "ckpt-13.data-00000-of-00001",
                                        "md5": "5a96886e53f98daae379787ee0f22bda"
                                    }
                                ],
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "artifact_name": "ckpt-13",
                                "create_date": 1673335822851,
                                "metric": {
                                    "total_loss": 0.548,
                                    "classification_loss": 0.511,
                                    "localization_loss": 0.006,
                                    "regularization_loss": 0.03
                                },
                                "is_deployed": false,
                                "exports": [],
                                "model_type": "efficientdet-d1-640x640"
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Artifact.retrieve("artifact_63bd140e67b42dc9f431ffe2")
        """
        return cls.request("GET", f"/artifact/{artifact_id}")

    @classmethod
    def list_exported(cls, artifact_id: str) -> dict:
        """Lists all exported models of a specific artifact.

        :param artifact_id: The ID of the artifact as a string.
        :return: A list of dictionaries with the exported model metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "id": "model_d15aba68872b045e27ac3db06a401da3",
                                "object": "model",
                                "status": "Finished",
                                "format": "tensorflow",
                                "create_date": 1673336054173,
                                "download": {
                                    "method": "GET",
                                    "expiry": 1673339505871,
                                    "url": "https://storage.googleapis.com/exports.datature.ioa2d89"
                                }
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Artifact.list_exported("artifact_63bd140e67b42dc9f431ffe2")
        """
        return cls.request(
            "GET",
            f"/artifact/{artifact_id}/models",
        )

    @classmethod
    def export_model(cls, artifact_id: str, model_format: str) -> dict:
        """Exports an artifact model in a specific model format.

        :param artifact_id: The ID of the artifact as a string.
        :param model_format: The export format of the model.

        :return: A dictionary containing the operation metadata of the model export with the following structure:

                .. code-block:: json

                            {
                                "id": "model_d15aba68872b045e27ac3db06a401da3",
                                "object": "model",
                                "status": "Running",
                                "format": "tensorflow",
                                "create_date": 1673336054173,
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Artifact.export_model(
                            "artifact_63bd140e67b42dc9f431ffe2", "tensorflow")
        """
        return cls.request("POST",
                           f"/artifact/{artifact_id}/export",
                           request_body={"format": model_format})
