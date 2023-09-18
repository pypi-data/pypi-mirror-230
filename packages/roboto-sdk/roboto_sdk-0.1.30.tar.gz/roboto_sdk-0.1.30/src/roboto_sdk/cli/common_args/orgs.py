#  Copyright (c) 2023 Roboto Technologies, Inc.

import argparse
import os

ORG_ARG_HELP = (
    "The org_id for the calling organization. Will be set implicitly "
    + "if the user is part of exactly one org. "
    + "Users can set a `ROBOTO_ORG_ID` environment variable to control the default value of this argument."
)

DEFAULT_ORG_ID = os.getenv("ROBOTO_ORG_ID")


def add_org_arg(parser: argparse.ArgumentParser, arg_help: str = ORG_ARG_HELP):
    parser.add_argument(
        "--org", required=False, type=str, help=arg_help, default=DEFAULT_ORG_ID
    )
