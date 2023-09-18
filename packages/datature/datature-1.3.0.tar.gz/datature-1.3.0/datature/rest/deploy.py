#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   Deploy.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Deploy API
'''

from datature.http.resource import RESTResource
from datature.rest.types import DeploymentMetadata


class Deploy(RESTResource):
    """Datature Deploy API Resource."""

    @classmethod
    def list(cls) -> dict:
        """Lists all deployments in a project.

        :return: A list of dictionaries containing deployment metadata with the following structure:

                .. code-block:: json

                        [{
                            "id": "deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b",
                            "object": "deploy",
                            "name": "My First API v2",
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "artifact_id": "artifact_63fd950a64845427a706d57c",
                            "version_tag": "car.staging.v3",
                            "scaling": {
                                "num_instances": 1,
                                "mode": "FixedReplicaCount"
                            },
                            "resources": {
                                "cpu": 8,
                                "ram": 8192,
                                "GPU_T4": 1
                            },
                            "status": {
                                "overview": "AVAILABLE",
                                "message": "Created service successfully",
                                "status_date": 1692853927419
                            },
                            "create_date": 1692853593947,
                            "last_modified_date": 1692853927444,
                            "url": "http://35.227.240.122/ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b/predict"
                        }]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Deploy.list()
        """
        return cls.request("GET", "/deploy/list")

    @classmethod
    def retrieve(cls, deploy_id: str) -> dict:
        """Retrieves a specific deployment using the deployment ID.

        :param deploy_id: The ID of the deployment as a string.
        :return: A dictionary containing the specific deployment metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b",
                            "object": "deploy",
                            "name": "My First API v2",
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "artifact_id": "artifact_63fd950a64845427a706d57c",
                            "version_tag": "car.staging.v3",
                            "scaling": {
                                "num_instances": 1,
                                "mode": "FixedReplicaCount"
                            },
                            "resources": {
                                "cpu": 8,
                                "ram": 8192,
                                "GPU_T4": 1
                            },
                            "status": {
                                "overview": "AVAILABLE",
                                "message": "Created service successfully",
                                "status_date": 1692853927419
                            },
                            "create_date": 1692853593947,
                            "last_modified_date": 1692853927444,
                            "url": "http://35.227.240.122/ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b/predict"
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Deploy.retrieve("deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b")
        """
        return cls.request("GET", f"/deploy/{deploy_id}")

    @classmethod
    def delete(cls, deploy_id: str) -> dict:
        """Deletes a specific deployment from the project.

        :param deploy_id: The id of the deployment.
        :return: A dictionary containing the deleted deployment ID and the deletion status with the following structure:

                .. code-block:: json

                            {
                                "id": "deploy_30922d5e-b2f6-43dc-b7b4-e29e2c30fb45",
                                "deleted": true
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Deploy.delete("deploy_30922d5e-b2f6-43dc-b7b4-e29e2c30fb45")
        """
        return cls.request("DELETE", f"/deploy/{deploy_id}")

    @classmethod
    def create(cls, deployment: DeploymentMetadata) -> dict:
        """Creates a deployment for a specific model using the model ID.

        :param deployment: The configuration metadata of the deployment.
        :return: A dictionary containing the specific deployment metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b",
                            "object": "deploy",
                            "name": "My First API",
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "artifact_id": "artifact_63fd950a64845427a706d57c",
                            "version_tag": "car.staging.v3",
                            "scaling": {
                                "num_instances": 1,
                                "mode": "FixedReplicaCount"
                            },
                            "resources": {
                                "cpu": 8,
                                "ram": 8192,
                                "GPU_T4": 1
                            },
                            "status": {
                                "overview": "AVAILABLE",
                                "message": "Created service successfully",
                                "status_date": 1692853927419
                            },
                            "create_date": 1692853593947,
                            "last_modified_date": 1692853927444,
                            "url": "http://35.227.240.122/ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b/predict"
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Deploy.create({
                            "name": "My First API",
                            "artifact_id": "artifact_63fd950a64845427a706d57c",
                            "num_of_instances": 1,
                            "version_tag": "car.staging.v3",
                        })
        """
        deployment_metadata = DeploymentMetadata(**deployment)

        return cls.request("POST",
                           "/deploy",
                           request_body=deployment_metadata.to_json())

    @classmethod
    def modify(cls, deploy_id: str, deployment: DeploymentMetadata) -> dict:
        """Creates a deployment for a specific model using the model ID.

        :param deploy_id: The ID of the deployment as a string.
        :param deployment: The configuration metadata of the deployment.
        :return: A dictionary containing the specific deployment metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b",
                            "object": "deploy",
                            "name": "My Second API",
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "artifact_id": "artifact_63fd950a64845427a706d57c",
                            "version_tag": "car.staging.v3",
                            "scaling": {
                                "num_instances": 1,
                                "mode": "FixedReplicaCount"
                            },
                            "resources": {
                                "cpu": 8,
                                "ram": 8192,
                                "GPU_T4": 1
                            },
                            "status": {
                                "overview": "UPDATING",
                                "message": "Created service successfully",
                                "status_date": 1692853927419
                            },
                            "create_date": 1692853593947,
                            "last_modified_date": 1692853927444,
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Deploy.modify(
                            "deploy_30922d5e-b2f6-43dc-b7b4-e29e2c30fb45",
                            {
                                "version_tag": "car.staging.v3",
                                "artifact_id": "artifact_63fd950a64845427a706d57d"
                            })
        """
        deployment_metadata = DeploymentMetadata(**deployment)

        return cls.request("PUT",
                           f"/deploy/{deploy_id}",
                           request_body=deployment_metadata.to_json())

    @classmethod
    def create_version(cls, deploy_id: str, version_tag: str, artifact_id: str) -> dict:
        """Updates a deployment version for a specific artifact using the artifact ID.

        :param deploy_id: The ID of the deployment as a string.
        :param version_tag: The new version tag name of the deployment.
        :param artifact_id: The ID of the artifact as a string.
        :return: A dictionary containing the specific deployment metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "deploy_ad0edd8b-c76a-4b4a-a1cb-f96fdfaf885b",
                            "object": "deploy",
                            "name": "My Second API",
                            "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                            "artifact_id": "artifact_63fd950a64845427a706d57d",
                            "version_tag": "car.staging.v4",
                            "scaling": {
                                "num_instances": 1,
                                "mode": "FixedReplicaCount"
                            },
                            "resources": {
                                "cpu": 8,
                                "ram": 8192,
                                "GPU_T4": 1
                            },
                            "status": {
                                "overview": "UPDATING",
                                "message": "Created service successfully",
                                "status_date": 1692853927419
                            },
                            "create_date": 1692853593947,
                            "last_modified_date": 1692853927444,
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Deploy.create_version(
                            "deploy_30922d5e-b2f6-43dc-b7b4-e29e2c30fb45",
                            "car.staging.v4",
                            "artifact_63fd950a64845427a706d57d"
                        )
        """
        return cls.request("POST",
                           f"/deploy/{deploy_id}/version",
                           request_body={
                               "versionTag": version_tag,
                               'artifactId': artifact_id,
                           })
