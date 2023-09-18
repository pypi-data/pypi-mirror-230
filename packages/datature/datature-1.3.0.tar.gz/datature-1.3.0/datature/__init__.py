#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   __init__.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   init module, include global configuration
'''
# autopep8: off
# Global Configuration
API_BASE_URL = "https://api.datature.io/v1"
SDK_VERSION = "1.3.0"

# Constant environment
OPERATION_LOOPING_TIMES = 20
ASSET_UPLOAD_BATCH_SIZE = 5000
SHOW_PROGRESS = False
OPERATION_LOOPING_DELAY_SECONDS = 5
HTTP_TIMEOUT_SECONDS = 120

# Set to either 'debug' or 'info'
LOG_LEVEL = None

# pylint: disable=C0103
secret_key = None

# API resources
# pylint: disable=C0413
from datature.rest import *
