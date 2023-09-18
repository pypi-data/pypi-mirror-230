#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   resource.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Base class for REST API resources
'''

from halo import Halo

import datature
from datature.http.requester import Requester
from datature.messages import REQUEST_SERVER_MESSAGE


# pylint: disable=R0913,R0903
class RESTResource():
    """Datature REST resource."""

    @classmethod
    def request(cls,
                method,
                url,
                query=None,
                request_body=None,
                request_headers=None,
                request_files=None):
        """Create a REST resource and make the http call."""
        request_spinner = None

        if datature.SHOW_PROGRESS:
            request_spinner = Halo(text=REQUEST_SERVER_MESSAGE, spinner='dots')
            request_spinner.start()

        response = Requester().request(method, url, query, request_body,
                                       request_headers, request_files)

        if request_spinner is not None:
            request_spinner.stop()

        return response
