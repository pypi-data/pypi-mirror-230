#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   test_run.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Run API Test Cases
'''

import unittest
from unittest.mock import MagicMock
from datature.rest.run import Run


class TestRun(unittest.TestCase):
    """Datature Run API Resource Test Cases."""

    def test_list(self):
        """Test list training."""
        Run.request = MagicMock()

        Run.list()

        Run.request.assert_called_once_with("GET", "/run/list")

    def test_retrieve(self):
        """Test retrieve a training."""
        Run.request = MagicMock()

        Run.retrieve("run_id")

        Run.request.assert_called_once_with("GET", "/run/run_id")

    def test_kill(self):
        """Test kill a training."""
        Run.request = MagicMock()

        Run.kill("run_id")

        Run.request.assert_called_once_with("PUT",
                                            "/run/run_id",
                                            request_body={"status": "killed"})

    def test_start(self):
        """Test start a training."""
        Run.request = MagicMock()

        Run.start(
            "flow_id", {
                "accelerator": {
                    "name": "GPU_T4",
                    "count": 1
                },
                "checkpoint": {
                    "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                    "evaluation_interval": 1,
                    "metric": "Loss/total_loss"
                },
                "limit": {
                    "metric": "LIM_MINUTE",
                    "value": 260
                },
                "preview": True,
                "matrix": True
            })

        Run.request.assert_called_once_with(
            "POST",
            "/run",
            request_body={
                "flowId": "flow_id",
                "execution": {
                    "accelerator": {
                        "name": "GPU_T4",
                        "count": 1
                    },
                    "checkpoint": {
                        "strategy": "STRAT_LOWEST_VALIDATION_LOSS",
                        "evaluationInterval": 1,
                        "metric": "Loss/total_loss"
                    },
                    "limit": {
                        "metric": "LIM_MINUTE",
                        "value": 260
                    },
                    "debug": None
                },
                "features": {
                    "preview": True,
                    "matrix": True
                }
            })

    def test_log(self):
        """Test retrieve a training log."""
        Run.request = MagicMock()

        Run.log("log_id")

        Run.request.assert_called_once_with("GET", "/run/log/log_id")

    def test_retrieve_confusion_matrix(self):
        """Test retrieve a training matrix."""
        Run.request = MagicMock()

        Run.retrieve_confusion_matrix("run_id")

        Run.request.assert_called_once_with(
            "GET", "/run/run_id/confusion-matrix")
