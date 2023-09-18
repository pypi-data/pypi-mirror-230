#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   workflow.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Workflow API
'''

from datature.rest.types import FlowMetadata
from datature.http.resource import RESTResource


class Workflow(RESTResource):
    """Datature Workflow API Resource."""

    @classmethod
    def list(cls) -> dict:
        """Lists all workflows in the project.

        :return: A list of dictionaries containing the workflow metadata with the following structure:

                .. code-block:: json

                            [
                                {
                                    "id": "flow_639309be08b4488a914b8802",
                                    "object": "workflow",
                                    "title": "My very awesome workflow",
                                    "state": "",
                                    "project_id": "proj_b705a30ae26671657f1fd51eb2d4739d",
                                    "last_updated": 1670581881299
                                }
                            ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Workflow.list()
        """
        return cls.request("GET", "/workflow/list")

    @classmethod
    def retrieve(cls, flow_id: str) -> dict:
        """Retrieves a specific workflow using the flow ID.

        :param flow_id: The ID of the workflow.
        :return: A dictionary containing the specific workflow metadata with the following structure:

                .. code-block:: json

                                {
                                    "id": "flow_639309be08b4488a914b8802",
                                    "object": "workflow",
                                    "title": "My very awesome workflow",
                                    "state": "",
                                    "project_id": "proj_b705a30ae26671657f1fd51eb2d4739d",
                                    "last_updated": 1670581881299
                                }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Workflow.retrieve("flow_639309be08b4488a914b8802")
        """
        return cls.request("GET", f"/workflow/{flow_id}")

    @classmethod
    def modify(cls, flow_id: str, flow: FlowMetadata) -> dict:
        """Updates title of a specific workflow using the flow ID.

        :param flow_id: The ID of the workflow.
        :param flow: The new metadata of the workflow to be updated.
        :return: A dictionary containing the updated workflow metadata with the following structure:

                .. code-block:: json

                                {
                                    "id": "flow_639309be08b4488a914b8802",
                                    "object": "workflow",
                                    "title": "My awesome workflow",
                                    "state": "",
                                    "project_id": "proj_b705a30ae26671657f1fd51eb2d4739d",
                                    "last_updated": 1670581881299
                                }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Workflow.modify(
                            "flow_639309be08b4488a914b8802", {"title": "My awesome workflow"})
        """
        return cls.request("PUT", f"/workflow/{flow_id}", request_body=flow)

    @classmethod
    def delete(cls, flow_id: str) -> dict:
        """Deletes a specific workflow using the flow ID.

        :param flow_id: The ID of the workflow
        :return: A dictionary containing the deleted workflow ID and deletion status with the following structure:

                .. code-block:: json

                                {
                                    "id": "flow_639309be08b4488a914b8802",
                                    "deleted":true
                                }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"
                        datature.Workflow.delete("flow_639309be08b4488a914b8802")
        """
        return cls.request("DELETE", f"/workflow/{flow_id}")
