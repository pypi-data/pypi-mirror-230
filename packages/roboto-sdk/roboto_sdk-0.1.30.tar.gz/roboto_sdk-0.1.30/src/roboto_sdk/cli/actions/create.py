#  Copyright (c) 2023 Roboto Technologies, Inc.
import argparse
import json
import sys

from ...domain.actions import Action
from ..command import (
    KeyValuePairsAction,
    RobotoCommand,
)
from ..common_args import (
    ActionParameterArg,
    ParseError,
    add_compute_requirements_args,
    add_container_parameters_args,
    add_org_arg,
    parse_compute_requirements,
    parse_container_overrides,
)
from ..context import CLIContext


def create(
    args: argparse.Namespace, context: CLIContext, parser: argparse.ArgumentParser
) -> None:
    try:
        compute_requirements = parse_compute_requirements(args)
        container_parameters = parse_container_overrides(args)
    except ParseError as exc:
        print(exc.msg, file=sys.stderr)
    else:
        action = Action.create(
            name=args.name,
            parameters=args.parameter,
            uri=args.image,
            description=args.description,
            compute_requirements=compute_requirements,
            container_parameters=container_parameters,
            metadata=args.metadata,
            tags=args.tag,
            action_delegate=context.actions,
            invocation_delegate=context.invocations,
            org_id=args.org,
        )

        print(f"Successfully created action '{action.name}'. Record: ")
        print(json.dumps(action.to_dict(), indent=4))


def create_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--name",
        required=True,
        action="store",
        help=(
            "Name of the action. Not modifiable after creation. "
            "An action is considered unique by its (name, docker_image_name, docker_image_tag) tuple."
        ),
    )
    parser.add_argument(
        "--description",
        required=False,
        action="store",
        help="Optional description of action. Modifiable after creation.",
    )
    parser.add_argument(
        "--image",
        required=False,
        action="store",
        dest="image",
        help="Associate a Docker image with this action. Modifiable after creation.",
    )
    parser.add_argument(
        "--parameter",
        required=False,
        metavar=ActionParameterArg.METAVAR,
        nargs="*",
        action=ActionParameterArg,
        help=(
            "Zero or more parameters (space-separated) accepted by this action. "
            "'name' is the only required attribute. "
            "'default' values, if provided, are JSON parsed. "
            "This argument can be specified multiple times. "
            "Parameters can be modified after creation. "
        ),
    )
    parser.add_argument(
        "--metadata",
        required=False,
        metavar="KEY=VALUE",
        nargs="*",
        action=KeyValuePairsAction,
        help=(
            "Zero or more 'key=value' format key/value pairs which represent action metadata. "
            "`value` is parsed as JSON. "
            "Metadata can be modified after creation."
        ),
    )
    parser.add_argument(
        "--tag",
        required=False,
        type=str,
        nargs="*",
        help="One or more tags to annotate this action. Modifiable after creation.",
        action="extend",
    )
    add_org_arg(parser=parser)

    add_compute_requirements_args(parser)
    add_container_parameters_args(parser)


create_command = RobotoCommand(
    name="create",
    logic=create,
    setup_parser=create_parser,
    command_kwargs={"help": "Create a new action."},
)
