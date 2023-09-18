#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   main.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   CLI main entrance
'''

import sys

import datature
from datature import messages
from datature.cli import functions
from datature.cli.commands import Commands
from datature.cli.config import Config
from datature.error import ErrorWithCode, ForbiddenError


# pylint: disable=R0912,R0915
def main() -> None:
    """
    Executes the main function of cli.

    """
    commands = Commands()
    args = commands.parse_args()

    try:
        # project secret management
        if args.command == "project":
            if args.action == "auth":
                functions.authenticate()
            elif args.action == "select":
                functions.select_project()
            elif args.action == "list":
                functions.list_projects()
            else:
                commands.print_help(args.command)

        else:
            # Get default project
            config = Config()
            project = config.get_default_project()
            if not project:
                print(messages.NO_PROJECT_MESSAGE)
                sys.exit(1)

            # Set project secret
            datature.secret_key = project.get("project_secret")

            if args.command == "asset":
                if args.action == "upload":
                    functions.upload_assets(args.path, args.groups)
                elif args.action == "group":
                    functions.assets_group(args.group)
                else:
                    commands.print_help(args.command)

            elif args.command == "annotation":
                if args.action == "upload":
                    functions.upload_annotations(args.path, args.format)
                elif args.action == "download":
                    functions.download_annotations(args.path, args.format)
                else:
                    commands.print_help(args.command)

            elif args.command == "artifact":
                if args.action == "download":
                    functions.download_artifact(args.artifact_id, args.format)
                else:
                    commands.print_help(args.command)
            else:
                commands.print_help()
    except KeyboardInterrupt:
        sys.exit(0)
    except ForbiddenError:
        print(messages.AUTHENTICATION_FAILED_MESSAGE)
        sys.exit(1)
    except ErrorWithCode:
        print(messages.UNKNOWN_ERROR_SUPPORT_MESSAGE)
        sys.exit(1)
    except IOError:
        print(messages.CONNECTION_ERROR_MESSAGE)
        sys.exit(1)
    except Exception as ex:  # pylint: disable=W0703
        print(f"\n{ex}")
        sys.exit(1)
