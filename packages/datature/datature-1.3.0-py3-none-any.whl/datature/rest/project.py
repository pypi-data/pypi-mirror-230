#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   project.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Project API
'''

from datature.http.resource import RESTResource
from datature.rest.types import ProjectMetadata


class Project(RESTResource):
    """Datature Project API Resource."""

    @classmethod
    def retrieve(cls) -> dict:
        """Retrieves project information.

        :return: A dictionary containing the project metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "object": "project",
                            "owner": "user_6323fea23e292439f31c58cd",
                            "name": "New Test Name",
                            "type": "classification",
                            "create_date": 1673253800069,
                            "localization": "MULTI",
                            "tags": [
                                "tagName1",
                                "tagName2"
                            ],
                            "statistic": {
                                "tags_count": [
                                    {
                                        "name": "tagName1",
                                        "count": 72
                                    },
                                    {
                                        "name": "tagName2",
                                        "count": 844
                                    }
                                ],
                                "asset_total": 50,
                                "asset_annotated": 50,
                                "annotation_total": 971
                            }
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Project.retrieve()
        """
        return cls.request("GET", "/project")

    @classmethod
    def modify(cls, project: ProjectMetadata) -> dict:
        """Updates the project name.

        :param project: The new metadata of the project to be updated.
        :return: A dictionary containing the project metadata and the updated project name with the following structure:

                .. code-block:: json

                        {
                            "id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "object": "project",
                            "owner": "user_6323fea23e292439f31c58cd",
                            "name": "New Test Name",
                            "type": "classification",
                            "create_date": 1673253800069,
                            "localization": "MULTI",
                            "tags": [
                                "tagName1",
                                "tagName2"
                            ],
                            "statistic": {
                                "tags_count": [
                                    {
                                        "name": "tagName1",
                                        "count": 72
                                    },
                                    {
                                        "name": "tagName2",
                                        "count": 844
                                    }
                                ],
                                "asset_total": 50,
                                "asset_annotated": 50,
                                "annotation_total": 971
                            }
                        }
        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Project.modify({"name":"My Cool Project"})
        """
        return cls.request("PUT", "/project", request_body=project)

    @classmethod
    def quota(cls) -> dict:
        """Retrieves the project quota showing the limits based on the tier the project account is on and the current usage.

        :return: A dictionary containing the project quota metadata with the following structure:

                .. code-block:: json

                        {
                            "limit": {
                                "collaborator": 3,
                                "image": 60000,
                                "compute": 20000,
                                "artifact": 50,
                                "artifact_export": 50,
                                "intellibrush": 0,
                                "external_source": 0,
                                "octopod": 2
                            },
                            "usage": {
                                "collaborator": 0,
                                "image": 35329,
                                "compute": 0,
                                "artifact": 7,
                                "artifact_export": 0,
                                "intellibrush": 0,
                                "external_source": 0,
                                "octopod": 0
                            }
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Project.quota()
        """
        return cls.request("GET", "/project/quota")

    @classmethod
    def insight(cls) -> dict:
        """Retrieves project insight and metrics of the completed training runs.

        :return: A dictionary containing the project insight metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "flow_title": "Blood Cell Detector",
                                "run_id": "run_63eb212ff0f856bf95085095",
                                "step": 600,
                                "create_date": 1676354685212,
                                "metric": {
                                    "total_loss": 0.433,
                                    "classification_loss": 0.39,
                                    "localization_loss": 0.013,
                                    "regularization_loss": 0.03
                                },
                                "statistic": {
                                    "average_annotations": 19.38
                                },
                                "optimizer": "momentum_optimizer",
                                "learning_rate": 0.08,
                                "momentum": 0.9,
                                "epochs": 3000,
                                "batch_size": 4,
                                "mode_name": "efficientdet-d1-640x640",
                                "max_detection_per_class": 30,
                                "data_type": "bbox",
                                "num_classes": 3,
                                "split_ratio": 0.2,
                                "shuffle": true,
                                "seed": 0,
                                "checkpoint_every_n": 100,
                                "metric_target": "Loss/total_loss"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Project.insight()
        """
        return cls.request("GET", "/project/insight")

    @classmethod
    def users(cls) -> dict:
        """Retrieves all users in the project. This includes Project Owners, Collaborators and Datature Experts.

        :return: A list of dictionaries containing the project user metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "id": "user_6323fea23e292439f31c58cd",
                                "object": "user",
                                "access_type": "owner",
                                "email": "xxx@datature.io",
                                "nickname": "xxx",
                                "picture": "https://s.gravatar.com/avatar/8608tars%2Fra.png"
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Project.users()
        """
        return cls.request("GET", "/project/users")
