#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   commands.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   CLI supported commands
'''

import sys
from argparse import ArgumentParser, _SubParsersAction
from typing import Optional

import datature


# pylint: disable = R0903,R0914
class Commands:
    """All Datature CLI commands."""

    def __init__(self) -> None:

        self.parser = ArgumentParser(
            prog='datature',
            description=
            "Command line tool to create/upload/download datasets on datature nexus.",
        )

        self.parser.add_argument('-v',
                                 '--version',
                                 action='version',
                                 version=('%(prog)s '
                                          f'{datature.SDK_VERSION}'))

        subparsers = self.parser.add_subparsers(dest="command")

        # Project
        project = subparsers.add_parser(
            "project",
            help="Project management.",
            description=
            "datature project - auth/list/select project from saved project.",
        )
        project_action = project.add_subparsers(dest="action")

        project_action.add_parser('auth',
                                  help='Authenticate and save the project.')
        project_action.add_parser(
            'select', help='Select the project from saved projects.')
        project_action.add_parser('list', help='List the saved projects.')
        project_action.add_parser('help',
                                  help='Show this help message and exit.',
                                  add_help=False)

        # Asset
        asset = subparsers.add_parser(
            "asset",
            help="Asset management.",
            description="datature asset - upload/group assets.")
        asset_action = asset.add_subparsers(dest="action")

        asset_upload = asset_action.add_parser('upload',
                                               help='Bulk update assets.')
        asset_upload.add_argument("path",
                                  nargs='*',
                                  help='The asset path to upload.')
        asset_upload.add_argument("groups",
                                  nargs='*',
                                  help='The asset groups to upload.')

        asset_group = asset_action.add_parser(
            'group', help='List assets group details.')
        asset_group.add_argument("group",
                                 nargs='*',
                                 help='The asset group name.')
        asset_action.add_parser('help',
                                help='Show this help message and exit.',
                                add_help=False)

        # Annotation
        annotation = subparsers.add_parser(
            "annotation",
            help="Annotation management.",
            description="datature annotation - upload/download annotations.")
        annotation_action = annotation.add_subparsers(dest="action")

        annotation_upload = annotation_action.add_parser(
            'upload', help='Bulk upload annotations from file.')
        annotation_upload.add_argument("path",
                                       nargs='*',
                                       help='The annotations file path.')
        annotation_upload.add_argument(
            "format", nargs='*', help='The annotations format to upload.')

        annotation_download = annotation_action.add_parser(
            'download', help='Bulk download annotations to file.')

        annotation_download.add_argument("path",
                                         nargs='*',
                                         help='The annotations file path.')
        annotation_download.add_argument(
            "format", nargs='*', help='The annotations format to download.')

        annotation_action.add_parser('help',
                                     help='Show this help message and exit.',
                                     add_help=False)

        # Artifact
        artifact = subparsers.add_parser(
            "artifact",
            help="Artifact management.",
            description="datature artifact - download artifact models.")

        artifact_action = artifact.add_subparsers(dest="action")
        artifact_download = artifact_action.add_parser(
            'download', help='Download artifact model.')
        artifact_download.add_argument("artifact_id",
                                       nargs='*',
                                       help='The id of the artifact.')
        artifact_download.add_argument("format",
                                       nargs='*',
                                       help='The artifact model formate.')

        artifact_action.add_parser('help',
                                   help='Show this help message and exit.',
                                   add_help=False)

        # Help
        help_parser = subparsers.add_parser(
            "help", description="Show this help message and exit.")
        help_action = help_parser.add_subparsers(dest="action")
        help_action.add_parser('project')
        help_action.add_parser('asset')
        help_action.add_parser('annotation')
        help_action.add_parser('artifact')

    def parse_args(self) -> ArgumentParser:
        """
        Parses and validates the CLI commands.

        :return: The parser to use.
        """
        args = self.parser.parse_args()

        if not args.command:
            self.print_help()
            sys.exit()

        return args

    # pylint: disable=W0212
    def print_help(self, subparser: Optional[str] = None):
        """
        Prints the help information.

        : param subparser: The name of subparser.
        :return: None
        """
        parser = self.parser

        if subparser:
            parser = next(action.choices[subparser]
                          for action in parser._actions
                          if isinstance(action, _SubParsersAction)
                          and subparser in action.choices)

        parser.print_help()
