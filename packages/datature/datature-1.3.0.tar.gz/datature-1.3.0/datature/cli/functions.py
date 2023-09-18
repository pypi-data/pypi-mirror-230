#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   functions.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   CLI functions
'''

import os
import re
import sys
import time
from os.path import basename, exists, join
from pathlib import Path
from typing import Optional

import inquirer
import requests
from halo import Halo
from alive_progress import alive_bar

import datature
from datature.utils import utils
from datature import error, messages
from datature.cli.config import Config
from datature.rest.types import AnnotationFormat

# pylint: disable=E1102

ASSET_UPLOAD_BATCH_SIZE = datature.ASSET_UPLOAD_BATCH_SIZE
datature.SHOW_PROGRESS = True

def authenticate():
    """
    Authenticate the Project Secret with the server and creates a configuration file for it.

    :param project_secret: Secret key to use for the client login.
    :return: None
    """
    project_secret = inquirer.password(message="Enter the project secret")

    project_secret = project_secret.strip()
    if project_secret == "":
        print(messages.AUTHENTICATION_REMINDER_MESSAGE)
        sys.exit(1)

    try:
        datature.secret_key = project_secret
        project = datature.Project.retrieve()

        project_name = project.get("name")
        project_id = project.get("id")

        default_project = inquirer.confirm(
            f"Make [{project_name}] the default project?", default=True)

        config = Config()
        config.set_project(project_id, project_name, project_secret,
                           default_project)

    except error.ForbiddenError:
        print(messages.INVALID_PROJECT_SECRET_MESSAGE)
        sys.exit(1)
    print(messages.AUTHENTICATION_MESSAGE)


def select_project():
    """
    Select project from saved configuration file.

    :return: None
    """
    config = Config()
    project_names = config.get_all_project_names()

    project_name = inquirer.list_input(
        "Which project do you want to select?",
        choices=project_names,
    )
    project = config.get_project_by_name(project_name)

    config.set_default_project(project.get("project_id"))
    print(f"{messages.ACTIVE_PROJECT_MESSAGE}: [{project_name}]")


def list_projects():
    """
    List projects from saved configuration file.

    :return: None
    """
    config = Config()
    project_names = config.get_all_project_names()
    default_project = config.get_default_project()

    output = [[
        "NAME", "TOTAL_ASSETS", "ANNOTATED_ASSETS", "ANNOTATIONS", "TAGS"
    ]]
    for project_name in project_names:
        project = config.get_project_by_name(project_name)
        try:
            datature.secret_key = project.get("project_secret")
            project = datature.Project.retrieve()
            asset_total = project.get("statistic").get("asset_total")
            asset_annotated = project.get("statistic").get("asset_annotated")
            annotation_total = project.get("statistic").get("annotation_total")
            tags = project.get("tags")
            output.append([
                project_name, asset_total, asset_annotated, annotation_total,
                len(tags)
            ])
        except error.ForbiddenError:
            print((
                f"\nProject {[project_name]} "
                "authentication failed, please use 'datature project auth' again."
            ))
            sys.exit(1)
    print_table(output, 20)
    print(
        f"\n{messages.ACTIVE_PROJECT_MESSAGE}: [{default_project.get('project_name')}]"
    )


def cli_loop_operation(op_link: str, data_size: int):
    """
    Upload annotations from path.

    :param path: The annotation path to upload.
    :param annotation_format: The annotation format to upload.
    :return: None
    """
    datature.SHOW_PROGRESS = False
    # Custom manage loop
    with alive_bar(data_size, title='Processing', title_length=12,
                   manual=True) as progress_bar:
        while True:
            operation = datature.Operation.retrieve(op_link)
            count = operation.get("status").get("progress").get("with_status")

            queued = count.get("queued")
            running = count.get("running")
            finished = count.get("finished")
            cancelled = count.get("cancelled")
            errored = count.get("errored")
            percentage = float(
                (int(errored) + int(cancelled) + int(finished)) /
                (int(errored) + int(cancelled) + int(finished) + int(queued) +
                 int(running)))

            if percentage == 1:
                break

            progress_bar(percentage)
            time.sleep(datature.OPERATION_LOOPING_DELAY_SECONDS)
        progress_bar(1.)
    print(messages.SERVER_COMPLETED_MESSAGE)
    datature.SHOW_PROGRESS = True


def upload_assets(path: Optional[Path] = None, groups: Optional[str] = None):
    """
    Upload assets from path.

    :param path: The folder to upload assets.
    :return: None
    """
    # check path if exist
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ASSETS_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    # find all images under folder and sub folders
    file_paths = utils.find_all_assets(path)

    if len(file_paths) == 0:
        print(messages.NO_ASSETS_FOUND_MESSAGE)
        sys.exit(1)

    nii_orientation = None
    if '.nii' in ",".join(str(file_path).lower() for file_path in file_paths):
        nii_orientation = inquirer.text(
            messages.ASSETS_NIFTI_DIRECTION_CHOICE_MESSAGE,
            validate=lambda _, x: x in ["", "x", "y", "z"],
        )

    if not groups:
        groups_res = inquirer.text(
            messages.ASSETS_GROUPS_MESSAGE,
            default="main",
            validate=lambda _, x: re.match("^[A-Za-z0-9,]*$", x),
        )
        groups = [
            group.strip() for group in groups_res.split(',') if group.strip()
        ]

    confirm = inquirer.confirm(
        f"{len(file_paths)} assets will be uploaded to group(s) ({', '.join(groups)})?",
        default=True)
    if not confirm:
        sys.exit(0)

    num_batches = len(file_paths) // ASSET_UPLOAD_BATCH_SIZE
    batches = [
        file_paths[i * ASSET_UPLOAD_BATCH_SIZE:(i + 1) *
                   ASSET_UPLOAD_BATCH_SIZE] for i in range(num_batches)
    ]

    if len(file_paths) % ASSET_UPLOAD_BATCH_SIZE != 0:
        batches.append(file_paths[num_batches * ASSET_UPLOAD_BATCH_SIZE:])

    # Loop Prepare asset metadata
    for _, batch in enumerate(batches):
        upload_session = datature.Asset.upload_session()

        with alive_bar(
                len(batch),
                title='Preparing',
                title_length=12,
        ) as progress_bar:
            for file_path in batch:
                upload_session.add(file_path, orientation=nii_orientation)
                progress_bar()

        operation = upload_session.start(groups)
        cli_loop_operation(operation.get("op_link"), upload_session.size())


def upload_annotations(path: Optional[Path] = None,
                       annotation_format: Optional[str] = None):
    """
    Upload annotations from path.

    :param path: The annotation path to upload.
    :param annotation_format: The annotation format to upload.
    :return: None
    """
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ANNOTATION_FOLDER_MESSAGE),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not annotation_format:
        questions = [
            inquirer.List(
                "annotation_format",
                message=messages.ANNOTATION_FORMAT_MESSAGE,
                choices=[format.value for format in AnnotationFormat],
            ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        annotation_format = answer.get("annotation_format")

    operation = datature.Annotation.upload(annotation_format, path)
    cli_loop_operation(operation.get("op_link"), 1)


def download_file_from_link(link: str, download_path: str):
    """
    Download file from link.

    :param link: The url link.
    :param download_path: The path to download file.
    :return: None
    """
    query_string_removed = link.split("?")[0]
    file_name = basename(query_string_removed)

    resp = requests.get(link,
                        stream=True,
                        timeout=datature.HTTP_TIMEOUT_SECONDS)

    total = int(resp.headers.get('content-length', 0))
    current_size = 0
    with open(join(download_path, file_name),
              'wb') as file, alive_bar(total,
                                       title='Downloading',
                                       title_length=12,
                                       manual=True) as progress_bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            current_size += size
            progress_bar(float(current_size / total))
        progress_bar(1.0)


# pylint: disable=R0912,R0914
def download_artifact(artifact_id: Optional[str] = None,
                      model_format: Optional[str] = None,
                      path: Optional[str] = None):
    """
    Download artifact model.

    :param artifact_id: The id of the artifact.
    :param model_format: The artifact model to download.
    :param path: The path to download the model.
    :return: None
    """
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.ARTIFACT_MODEL_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    if not artifact_id:
        # call server to list all artifacts
        artifacts = datature.Artifact.list()
        if len(artifacts) == 0:
            print(messages.NO_ARTIFACTS_MESSAGE)
            sys.exit(1)

        artifact_lists = []
        artifacts_key_map = {}
        for artifact in artifacts:
            key = (
                f"{artifact.get('run_id')[-6:].upper()}-{artifact.get('flow_title')}"
            )
            artifact_lists.append(key)
            artifacts_key_map[key] = artifact

        questions = [
            inquirer.List(
                "artifact",
                message=messages.ARTIFACT_DOWNLOAD_MESSAGE,
                choices=artifact_lists,
            ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        artifact_key = answer.get("artifact")
        artifact = artifacts_key_map.get(artifact_key)

    if not model_format:
        questions = [
            inquirer.List(
                "model_format",
                message=messages.ARTIFACT_MODEL_FORMAT_DOWNLOAD_MESSAGE,
                choices=artifact.get("exportable_formats", []),
            ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        model_format = answer.get("model_format")

    if model_format in artifact.get("exports"):
        # already exported, can download directly
        models = datature.Artifact.list_exported(artifact.get("id"))
        for model in models:
            if model.get("format") == model_format and model.get(
                    "status") == "Finished":

                download_file_from_link(model.get("download").get("url"), path)
    else:
        # already exported, can download directly
        datature.SHOW_PROGRESS = False
        # Loop to query status,
        wait_spinner = Halo(text=messages.EXPORT_ARTIFACT_WAITING_MESSAGE,
                            spinner='dots')
        wait_spinner.start()
        models = datature.Artifact.export_model(artifact.get("id"),
                                                model_format)

        while True:
            models = datature.Artifact.list_exported(artifact.get("id"))
            for model in models:
                if model.get("format") == model_format and model.get(
                        "status") == "Finished":
                    # start download
                    wait_spinner.stop()
                    download_file_from_link(
                        model.get("download").get("url"), path)

                    return

            time.sleep(datature.OPERATION_LOOPING_DELAY_SECONDS)


def download_annotations(path: Optional[Path] = None,
                         annotation_format: Optional[str] = None):
    """
    Export annotations from path.

    :param path: The annotation path to export.
    :param annotation_format: The annotation format to export.
    :return: None
    """
    if not path:
        questions = [
            inquirer.Path("path_result",
                          message=messages.EXPORT_ANNOTATION_FOLDER_MESSAGE,
                          default=os.getcwd()),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        path = answer.get("path_result").strip()

    if not exists(path):
        print(messages.PATH_NOT_EXISTS_MESSAGE)
        sys.exit(1)

    if not annotation_format:
        questions = [
            inquirer.List(
                "annotation_format",
                message=messages.ANNOTATION_FORMAT_MESSAGE,
                choices=[format.value for format in AnnotationFormat],
            ),
            inquirer.Text(
                "normalized",
                message=messages.DOWNLOAD_ANNOTATIONS_NORMALIZED_MESSAGE),
            inquirer.Text(
                "shuffle",
                message=messages.DOWNLOAD_ANNOTATIONS_SHUFFLE_MESSAGE),
            inquirer.Text(
                "split_ratio",
                message=messages.DOWNLOAD_ANNOTATIONS_SPLIT_RATIO_MESSAGE),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        annotation_format = answer.get("annotation_format")
        normalized = answer.get("normalized") not in ["n", "N"]
        shuffle = answer.get("shuffle") not in ["n", "N"]
        split_ratio = float(answer.get("split_ratio"))

        if split_ratio < 0 or split_ratio > 1:
            print(messages.INVALID_SPLIT_RATIO_MESSAGE)
            sys.exit(1)

    # Loop to query status,
    datature.SHOW_PROGRESS = False
    wait_spinner = Halo(text=messages.ANNOTATION_DOWNLOAD_MESSAGE,
                        spinner='dots')
    wait_spinner.start()
    operation = datature.Annotation.export(annotation_format,
                                           export_options={
                                               "normalized": normalized,
                                               "shuffle": shuffle,
                                               "split_ratio": split_ratio,
                                               "seed": 1337
                                           },
                                           background=True)
    wait_spinner.stop()
    cli_loop_operation(operation.get("op_link"), 1)
    annotation = datature.Annotation.retrieve_exported_file(
        operation.get("id"))
    download_file_from_link(annotation.get("download").get("url"), path)


def print_table(data: [[str]], column_width: int = 16):
    """
        List assets group statistics.

        :param data: The element array.
        :param column_width: The column widths and separator characters
        :return: None
        """
    # Print the table header
    print("".join(f"{item:{column_width}}" for _, item in enumerate(data[0])))

    # Print the table data
    for row in data[1:]:
        print("".join(f"{str(item):{column_width}}"
                      for _, item in enumerate(row)))


def assets_group(group: Optional[str] = None):
    """
    List assets group statistics.

    :param group: The name of group.
    :return: None
    """
    if not group:
        project = datature.Project.retrieve()

        groups = project.get("groups")
        if groups is None or len(groups) == 0:
            print(messages.NO_ASSETS_GROUP_MESSAGE)
            sys.exit(1)

        group = inquirer.list_input(
            messages.CHOOSE_GROUP_MESSAGE,
            choices=groups,
        )

        statistics = datature.Asset.group(group)
        statistic = statistics[0].get("statistic")

        table = [[
            "NAME", "TOTAL", "ANNOTATED", "REVIEW", "TOFIX", "COMPLETED"
        ]]
        table.append([
            group, statistic['asset_total'], statistic['asset_annotated'],
            statistic['asset_reviewed'], statistic['asset_tofixed'],
            statistic['asset_completed']
        ])
        print_table(table)
