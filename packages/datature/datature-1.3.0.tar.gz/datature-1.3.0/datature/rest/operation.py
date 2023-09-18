#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   operation.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Operation API
'''

import time

import datature
from datature import error, logger
from datature.http.resource import RESTResource


class Operation(RESTResource):
    """Datature Operation API Resource."""

    @classmethod
    def retrieve(cls, op_link: str) -> dict:
        """Retrieves an executed operation status using the operation link.

        :param op_link: The link of the operation as a string.
        :return: A dictionary containing the operation metadata with the following structure.

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

                        datature.Operation.retrieve("users/api|affaf/proje-1dca99b80024")
        """
        return cls.request("GET", "/operation", query={"opLink": op_link})

    @classmethod
    def loop_retrieve(
            cls,
            op_link: str,
            loop_times: int = datature.OPERATION_LOOPING_TIMES) -> dict:
        """Continuously retrieves an executed operation status for a specified number of times at a specified delay interval. Can be used to poll a running operation to monitor execution status.

        :param op_link: The link of the operation as a string.
        :param loop_times: The maximum number of times to loop the operation retrieval.
        :return: The operation status metadata if the operation has finished, a BadRequestError if the operation has errored out, or None if the operation is still running.

        :example:
                .. code-block:: python

                        import datature

                        datature.secret_key = "5aa41e8ba........"

                        datature.Operation.loop_retrieve("users/api|affaf/proje-1dca99b80024", 10)
        """
        # classification_tfrecord requires more processing time.
        # returns a response even if the operation has not finished when the loop ends.
        response = None
        for _ in range(loop_times):
            response = cls.request("GET",
                                   "/operation",
                                   query={"opLink": op_link})

            logger.log_info("Operation status:", status=response["status"])

            if response["status"]["overview"] == "Finished":
                return response

            if response["status"]["overview"] == "Errored":
                logger.log_info("Operation error: please contacts our support")

                raise error.BadRequestError(
                    "Operation error: please contacts our support")

            time.sleep(datature.OPERATION_LOOPING_DELAY_SECONDS)
        return response
