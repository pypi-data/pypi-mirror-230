#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   utils.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Utils Class module
'''

import os
import glob
from pathlib import Path
from os.path import isdir, isfile

from datature.error import Error

SUPPORTED_FILE_EXTENSIONS = [
    '*.jpg', '*.JPG', '*.png', '*.PNG', '*.jpeg', '*.JPEG', '*.mp4', '*.MP4',
    "*.dcm", "*.DCM", '*.nii', '*.NII'
]

ANNOTATION_FORMAT_EXTENSIONS_MAPPING = {
    "coco": ["*.json"],
    "csv_fourcorner": ["*.csv"],
    "csv_widthheight": ["*.csv"],
    "pascal_voc": ["*.xml"],
    "yolo_darknet": ["*.labels", "*.txt"],
    "yolo_keras_pytorch": ["*.txt"],
    "createml": ["*.json"],
    "polygon_coco": ["*.json"],
    "polygon_single": ["*.json"],
    "csv_classification": ["*.csv"],
}


def get_asset_metadata_limit_by_tier(tier: str) -> int:
    """Get asset limit by tier.

    :param tier: the tier of the project owner
    :return: limit in bytes
    """
    # professional tier 0.5kb
    if tier == "professional":
        return 500
    # developer tier 0.3kb
    if tier == "developer":
        return 300
    # free tier 0kb
    return 0


def find_all_assets(path: Path) -> [str]:
    """
    List all assets under folder, include sub folder.

    :param path: The folder to upload assets.
    :return: assets path list.
    """
    file_paths = []

    # find all assets under folder and sub folders
    for file_ext in SUPPORTED_FILE_EXTENSIONS:
        file_paths.extend(
            glob.glob(os.path.join(path, '**', file_ext), recursive=True))

    return file_paths


def find_all_annotations_files(path: Path, annotation_format: str) -> [str]:
    """
    List all annotations files under folder, include sub folder.

    :param path: The folder to upload annotations files.
    :param annotation_format: The format of the annotation type.
    :return: assets path list.
    """
    file_extensions = ANNOTATION_FORMAT_EXTENSIONS_MAPPING.get(
        annotation_format)

    if not file_extensions:
        raise Error("The annotation format is not valid")

    file_paths = []
    if isfile(path):
        file_paths.append(path)
    elif isdir(path):
        for file_ext in file_extensions:
            file_paths.extend(
                glob.glob(os.path.join(path, '**', file_ext), recursive=True))

    if len(file_paths) <= 0:
        raise Error("Could not find the annotation file")

    return file_paths
