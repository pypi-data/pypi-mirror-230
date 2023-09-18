#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   logger.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   logger module
'''

import sys
import logging

import datature

logger = logging.getLogger("datature")


def _console_log_level():
    """Get log level"""

    if datature.LOG_LEVEL in ["debug", "info"]:
        return datature.LOG_LEVEL
    return None


def log_debug(message, **params):
    """Only print to sys.stderr when log level is debug"""

    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def log_info(message, **params):
    """Print to sys.stderr """

    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)
    logger.info(msg)


def logfmt(props):
    """format log messages"""

    return " ".join([f"{key}={value}" for key, value in props.items()])
