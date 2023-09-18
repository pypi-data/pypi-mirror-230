#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   run.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Run API
'''

from datature.http.resource import RESTResource
from datature.rest.types import RunSetupMetadata


class Run(RESTResource):
    """Datature Run API Resource."""

    @classmethod
    def list(cls) -> dict:
        """Lists all training runs regardless of status.

        :return: A list of dictionaries containing the training run metadata with the following structure:

                .. code-block:: json

                        [
                            {
                                "id": "run_63eb212ff0f856bf95085095",
                                "object": "run",
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "flow_id": "flow_63bbd3bf8a78eb906f417396",
                                "status": {
                                    "conditions": [
                                        {
                                            "condition": "TrainingStarted",
                                            "last_updated": 1676353954729,
                                            "status": "finished"
                                        },
                                        {
                                            "condition": "TrainingFinished",
                                            "last_updated": 1676356061724,
                                            "status": "finished"
                                        }
                                    ],
                                    "last_updated": 1676356061724
                                },
                                "execution": {
                                    "accelerator": {
                                        "name": "GPU_T4",
                                        "count": 2
                                    },
                                    "checkpoint": {
                                        "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                                        "evaluation_interval": 100,
                                        "metric": "Loss/total_loss"
                                    }
                                },
                                "features": {
                                    "preview": true,
                                    "matrix": true
                                },
                                "create_date": 1676353954729,
                                "last_modified_date": 1676356061724,
                                "logs": [
                                    "log_63eb212ff0f856bf95085095"
                                ]
                            }
                        ]

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Run.list()
        """
        return cls.request("GET", "/run/list")

    @classmethod
    def retrieve(cls, run_id: str) -> dict:
        """Retrieves a specific training run using the run ID.

        :param run_id: The ID of the training run.
        :return: A dictionary containing the specific training run metadata with the following structure:

                .. code-block:: json

                            {
                                "id": "run_63eb212ff0f856bf95085095",
                                "object": "run",
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "flow_id": "flow_63bbd3bf8a78eb906f417396",
                                "status": {
                                    "conditions": [
                                        {
                                            "condition": "TrainingStarted",
                                            "last_updated": 1676353954729,
                                            "status": "finished"
                                        },
                                        {
                                            "condition": "TrainingFinished",
                                            "last_updated": 1676356061724,
                                            "status": "finished"
                                        }
                                    ],
                                    "last_updated": 1676356061724
                                },
                                "execution": {
                                    "accelerator": {
                                        "name": "GPU_T4",
                                        "count": 2
                                    },
                                    "checkpoint": {
                                        "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                                        "evaluation_interval": 100,
                                        "metric": "Loss/total_loss"
                                    }
                                },
                                "features": {
                                    "preview": true,
                                    "matrix": true
                                },
                                "create_date": 1676353954729,
                                "last_modified_date": 1676356061724,
                                "logs": [
                                    "log_63eb212ff0f856bf95085095"
                                ]
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Run.retrieve("run_63eb212ff0f856bf95085095")
        """
        return cls.request("GET", f"/run/{run_id}")

    @classmethod
    def kill(cls, run_id: str) -> dict:
        """Kills a specific training run using the run ID.

        :param run_id: The ID of the training run.
        :return: A dictionary containing the killed training metadata with the following structure:

                .. code-block:: json

                            {
                                "id": "run_63eb212ff0f856bf95085095",
                                "object": "run",
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "flow_id": "flow_63bbd3bf8a78eb906f417396",
                                "status": {
                                    "conditions": [
                                        {
                                            "condition": "TrainingStarted",
                                            "last_updated": 1676353954729,
                                            "status": "finished"
                                        },
                                        {
                                            "condition": "TrainingFinished",
                                            "last_updated": 1676356061724,
                                            "status": "killed"
                                        }
                                    ],
                                    "last_updated": 1676356061724
                                },
                                "execution": {
                                    "accelerator": {
                                        "name": "GPU_T4",
                                        "count": 2
                                    },
                                    "checkpoint": {
                                        "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                                        "evaluation_interval": 100,
                                        "metric": "Loss/total_loss"
                                    }
                                },
                                "features": {
                                    "preview": true,
                                    "matrix": true
                                },
                                "create_date": 1676353954729,
                                "last_modified_date": 1676356061724,
                                "logs": [
                                    "log_63eb212ff0f856bf95085095"
                                ]
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Run.kill("run_63eb212ff0f856bf95085095")
        """
        return cls.request("PUT",
                           f"/run/{run_id}",
                           request_body={"status": "killed"})

    @classmethod
    def start(cls, flow_id: str, setup: RunSetupMetadata) -> dict:
        """Starts a new training run from a specific workflow using the flow ID.

        :param flow_id: The ID of the workflow.
        :param setup: The metadata of the training.
        :return: A dictionary containing the newly-initialized training run metadata with the following structure:

                .. code-block:: json

                            {
                                "id": "run_63eb212ff0f856bf95085095",
                                "object": "run",
                                "project_id": "proj_cd067221d5a6e4007ccbb4afb5966535",
                                "flow_id": "flow_63bbd3bf8a78eb906f417396",
                                "status": {
                                    "conditions": [
                                        {
                                            "condition": "TrainingStarted",
                                            "last_updated": 1676353954729,
                                            "status": "finished"
                                        },
                                        {
                                            "condition": "TrainingFinished",
                                            "last_updated": 1676356061724,
                                            "status": "finished"
                                        }
                                    ],
                                    "last_updated": 1676356061724
                                },
                                "execution": {
                                    "accelerator": {
                                        "name": "GPU_T4",
                                        "count": 2
                                    },
                                    "checkpoint": {
                                        "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                                        "evaluation_interval": 100,
                                        "metric": "Loss/total_loss"
                                    }
                                },
                                "features": {
                                    "preview": true,
                                    "matrix": true
                                },
                                "create_date": 1676353954729,
                                "last_modified_date": 1676356061724,
                                "logs": [
                                    "log_63eb212ff0f856bf95085095"
                                ]
                            }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Run.start("flow_63d0f2d5fb1f9189db9b1c4b", {
                            "accelerator": {
                                "name": "GPU_T4",
                                "count": 1
                            },
                            "checkpoint": {
                                "strategy": "STRAT_ALWAYS_SAVE_LATEST",
                                "evaluation_interval": 1
                            },
                            "limit": {
                                "metric": "LIM_NONE",
                                "value": 0
                            },
                            "preview": true,
                            "matrix": true
                        })
        """
        return cls.request(
            "POST",
            "/run",
            request_body={
                "flowId": flow_id,
                "execution": {
                    "accelerator": {
                        "name": setup.get("accelerator").get("name"),
                        "count": setup.get("accelerator").get("count"),
                    },
                    "checkpoint": {
                        "strategy":
                        setup.get("checkpoint").get("strategy"),
                        "evaluationInterval":
                        setup.get("checkpoint").get("evaluation_interval"),
                        "metric":
                        setup.get("checkpoint").get("metric"),
                    },
                    "limit": {
                        "metric": setup.get("limit").get("metric"),
                        "value": setup.get("limit").get("value"),
                    },
                    "debug": setup.get("debug"),
                },
                "features": {
                    "preview": setup.get("preview", True),
                    "matrix": setup.get("matrix", True)
                }
            })

    @classmethod
    def log(cls, log_id: str) -> dict:
        """Retrieves a specific training log using the log ID.

        :param log_id: The ID of the training log.
        :return: A dictionary with the specific training log metadata with the following structure:

                .. code-block:: json

                        {
                            "id": "log_63eb212ff0f856bf95085095",
                            "object": "log",
                            "event": [
                                {
                                    "ev": "memoryUsage",
                                    "pl": {},
                                    "t": 1675669392000
                                }
                            ]
                        }

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Run.logs("log_63eb212ff0f856bf95085095")
        """
        return cls.request("GET", f"/run/log/{log_id}")

    @classmethod
    def retrieve_confusion_matrix(cls, run_id: str) -> dict:
        """Retrieves a training confusion matrix using the run ID.

        :param run_id: The ID of the training run.
        :return: A dictionary containing the specific training matrix json string with the following structure:
                .. code-block:: json
                        {
                            "type": "confusion-matrix",
                            "data": "{\"0\":[{\"id\":\"RBC\",\"data\":[{\"x\":\"RBC\",\"y\":0},{\"x\":\"WBC\",\"y\":0},{\"x\":\"Platelets\",\"y\":0},{\"x\":\"boat\",\"y\":0},{\"x\":\"Background\",\"y\":0}]},{\"id\":\"WBC\",\"data\":[{\"x\":\"RBC\",\"y\":0},{\"x\":\"WBC\",\"y\":0},{\"x\":\"Platelets\",\"y\":0},{\"x\":\"boat\",\"y\":0},{\"x\":\"Background\",\"y\":0}]},{\"id\":\"Platelets\",\"data\":[{\"x\":\"RBC\",\"y\":0},{\"x\":\"WBC\",\"y\":0},{\"x\":\"Platelets\",\"y\":0},{\"x\":\"boat\",\"y\":0},{\"x\":\"Background\",\"y\":0}]},{\"id\":\"boat\",\"data\":[{\"x\":\"RBC\",\"y\":0},{\"x\":\"WBC\",\"y\":0},{\"x\":\"Platelets\",\"y\":0},{\"x\":\"boat\",\"y\":0},{\"x\":\"Background\",\"y\":0}]},{\"id\":\"Background\",\"data\":[{\"x\":\"RBC\",\"y\":302},{\"x\":\"WBC\",\"y\":27},{\"x\":\"Platelets\",\"y\":22},{\"x\":\"boat\",\"y\":2},{\"x\":\"Background\",\"y\":0}]}]}"
                        }
        :example:
                .. code-block:: python

                        import datature
                        datature.secret_key = "5aa41e8ba........"
                        datature.Run.retrieve_confusion_matrix("run_63eb212ff0f856bf95085095")
        """
        return cls.request("GET", f"/run/{run_id}/confusion-matrix")
