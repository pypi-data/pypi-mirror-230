#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   operation_fixture.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Operation Test Data
'''

pending_operation_response = {
    'id': 'op_c26ea31d-599c-4a03-8b0d-b2bc9995fa8a',
    'op_link': 'users/s/nexus.assets.upload/c26ea3bc9995fa8a',
    'status': {
        'overview': 'Running',
        'message': 'Operation running',
        'time_updated': 1669282308213,
        'time_scheduled': 1669281995881,
        'progress': {
            'unit': 'asset',
            'with_status': {
                'queued': 10,
                'running': 0,
                'finished': 436,
                'errored': 0,
                'cancelled': 0
            }
        }
    }
}

finished_operation_response = {
    'id': 'op_c26ea31d-599c-4a03-8b0d-b2bc9995fa8a',
    'op_link': 'users/s/nexus.assets.upload/c26ea3bc9995fa8a',
    'status': {
        'overview': 'Finished',
        'message': 'Operation running',
        'time_updated': 1669282308213,
        'time_scheduled': 1669281995881,
        'progress': {
            'unit': 'asset',
            'with_status': {
                'queued': 0,
                'running': 0,
                'finished': 436,
                'errored': 0,
                'cancelled': 0
            }
        }
    }
}

errored_operation_response = {
    'id': 'op_c26ea31d-599c-4a03-8b0d-b2bc9995fa8a',
    'op_link': 'users/s/nexus.assets.upload/c26ea3bc9995fa8a',
    'status': {
        'overview': 'Errored',
        'message': 'Operation running',
        'time_updated': 1669282308213,
        'time_scheduled': 1669281995881,
        'progress': {
            'unit': 'asset',
            'with_status': {
                'queued': 0,
                'running': 0,
                'finished': 436,
                'errored': 0,
                'cancelled': 0
            }
        }
    }
}
