#  Copyright (c) 2023 Roboto Technologies, Inc.

import argparse
import json
import sys
import textwrap
from typing import Any, Optional

from ...domain.actions import (
    Action,
    ComputeRequirements,
    ContainerParameters,
)
from ...domain.triggers import (
    Trigger,
    TriggerForEachPrimitive,
)
from ...query import (
    Comparator,
    Condition,
    ConditionGroup,
    ConditionOperator,
    ConditionType,
    QuerySpecification,
)
from ...sentinels import NotSet, value_or_not_set
from ..command import (
    JsonFileOrStrType,
    KeyValuePairsAction,
    RobotoCommand,
    RobotoCommandSet,
)
from ..common_args import (
    ParseError,
    add_compute_requirements_args,
    add_container_parameters_args,
    add_org_arg,
    parse_compute_requirements,
    parse_container_overrides,
)
from ..context import CLIContext

NAME_PARAM_HELP = "The unique name used to reference a trigger."
ACTION_NAME_PARAM_HELP = (
    "The unique name used to reference an action which a certain trigger invokes."
)


def parse_condition(
    args, context: CLIContext, parser: argparse.ArgumentParser
) -> Optional[ConditionType]:
    if args.condition_json and (args.required_tag or args.required_metadata):
        parser.error(
            "Can only specify '--condition-json' or a combination of '--required-tag' and "
            + "'--required-metadata' expressions, providing both does not work."
        )

    if args.condition_json:
        condition_json: dict[str, Any] = args.condition_json
        if "operator" in condition_json.keys():
            return ConditionGroup.parse_obj(condition_json)
        elif "comparator" in condition_json.keys():
            return Condition.parse_obj(condition_json)
        else:
            parser.error(
                "Provided '--condition-json' could not be parsed as a Condition or a ConditionGroup."
            )

    if args.required_tag or args.required_metadata:
        conditions = []
        if args.required_tag:
            for tag in args.required_tag:
                conditions.append(
                    Condition(field="tags", comparator=Comparator.Contains, value=tag)
                )

        if args.required_metadata:
            for key, value in args.required_metadata.items():
                conditions.append(
                    Condition(
                        field=f"metadata.{key}",
                        comparator=Comparator.Equals,
                        value=value,
                    )
                )

        return ConditionGroup(operator=ConditionOperator.And, conditions=conditions)

    return None


def parse_overrides(
    args, context: CLIContext, parser: argparse.ArgumentParser
) -> tuple[Optional[ComputeRequirements], Optional[ContainerParameters]]:
    if args.action_name is None:
        return None, None

    action = Action.from_name(
        name=args.action_name,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        org_id=args.org,
    )

    try:
        compute_requirement_overrides = None
        if args.vcpu is not None or args.memory is not None or args.storage is not None:
            compute_requirement_overrides = parse_compute_requirements(
                args=args,
                default_vcpu=action.compute_requirements.vCPU,
                default_memory=action.compute_requirements.memory,
                default_storage=action.compute_requirements.storage,
            )

        container_overrides = None
        if (
            args.entry_point is not None
            or args.command is not None
            or args.env is not None
            or args.workdir is not None
        ):
            container_overrides = parse_container_overrides(
                args,
                default_entry_point=action.container_parameters.entry_point,
                default_command=action.container_parameters.command,
                default_env_vars=action.container_parameters.env_vars,
                default_workdir=action.container_parameters.workdir,
            )

        return compute_requirement_overrides, container_overrides
    except ParseError as exc:
        print(exc.msg, file=sys.stderr)
        sys.exit(1)


def create(args, context: CLIContext, parser: argparse.ArgumentParser):
    condition = parse_condition(args, context, parser)

    compute_requirement_overrides, container_overrides = parse_overrides(
        args, context, parser
    )

    record = Trigger.create(
        name=args.name,
        action_name=args.action_name,
        org_id=args.org,
        required_inputs=args.input_data,
        condition=condition,
        for_each=args.for_each,
        compute_requirement_overrides=compute_requirement_overrides,
        container_parameter_overrides=container_overrides,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        trigger_delegate=context.triggers,
        additional_inputs=args.additional_inputs,
    )
    sys.stdout.write(json.dumps(record.to_dict()) + "\n")


def create_setup_parser(parser):
    parser.add_argument("--name", type=str, required=True, help=NAME_PARAM_HELP)
    parser.add_argument(
        "--action-name", type=str, required=True, help=ACTION_NAME_PARAM_HELP
    )
    parser.add_argument(
        "--required-inputs",
        required=True,
        dest="input_data",
        type=str,
        nargs="+",
        action="extend",
        # fmt: off
        help=textwrap.dedent("""\
            One or many file patterns for data to download from the data source. Examples:
                front camera images, "--input-data '**/cam_front/*.jpg'";
                front and rear camera images, "--input-data '**/cam_front/*.jpg' --input-data '**/cam_rear/*.jpg'";
                all data, "--input-data '**/*'"
        """),
        # fmt: on
    )
    parser.add_argument(
        "--additional-inputs",
        dest="additional_inputs",
        type=str,
        nargs="+",
        action="extend",
        # fmt: off
        help=textwrap.dedent("""\
            One or many file patterns for data to download from the data source which is NOT considered as part of
            trigger evaluation. Examples:
                front and rear camera images, "--input-data '**/cam_front/*.jpg' --input-data '**/cam_rear/*.jpg'";
                all data, "--input-data '**/*'"
        """),
        # fmt: on
    )
    add_org_arg(parser=parser)
    add_compute_requirements_args(parser)
    add_container_parameters_args(parser)
    parser.add_argument(
        "--for-each",
        type=TriggerForEachPrimitive,
        help="Primitive against which this trigger will spawn invocations.",
        default=TriggerForEachPrimitive.Dataset,
        choices=[x.value for x in TriggerForEachPrimitive],
    )
    parser.add_argument(
        "--condition-json",
        type=JsonFileOrStrType,
        help="Inline JSON or a reference to a JSON file "
        + "which expresses a dataset metadata and tag condition which must be met for this trigger "
        + "to run against a given dataset. If provided, 'required-tag' and 'required-metadata' cannot "
        + "be provided.",
    )
    parser.add_argument(
        "--required-tag",
        nargs="*",
        action="extend",
        help="Dataset tags which must be present for "
        + "this trigger to run against a given dataset. If provided, these are used to construct a "
        + "trigger condition, and as such they cannot be used if 'condition-json' is specified.",
    )
    parser.add_argument(
        "--required-metadata",
        nargs="*",
        action=KeyValuePairsAction,
        help="Dataset metadata "
        + "key=value conditions which all must be met for this trigger to run against a given dataset. "
        + "If provided, these are used to construct a trigger condition, and as such they cannot be "
        + "used if 'condition-json' is specified.",
    )


def update(args, context: CLIContext, parser: argparse.ArgumentParser):
    if args.enabled and args.disabled:
        parser.error("Cannot set both --enabled and --disabled!")

    if (
        args.condition_json or args.required_tag or args.required_metadata
    ) and args.clear_condition:
        parser.error(
            "Cannot specify a condition via '--required-tag', '--required-metadata', or '--condition-json', and "
            + "also clear the condition with '--clear-condition'."
        )

    condition = parse_condition(args, context, parser)

    compute_requirement_overrides, container_overrides = parse_overrides(
        args, context, parser
    )

    trigger = Trigger.from_name(
        name=args.name,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        trigger_delegate=context.triggers,
        org_id=args.org,
    )

    updates: dict[str, Any] = {
        "action_name": value_or_not_set(args.action_name),
        "required_inputs": value_or_not_set(args.required_inputs),
        "condition": None if args.clear_condition else value_or_not_set(condition),
        "additional_inputs": value_or_not_set(args.additional_inputs),
        "compute_requirement_overrides": value_or_not_set(
            compute_requirement_overrides
        ),
        "container_parameter_overrides": value_or_not_set(container_overrides),
        "for_each": value_or_not_set(args.for_each),
    }

    if args.enabled:
        updates["enabled"] = True
    elif args.disabled:
        updates["enabled"] = False
    else:
        updates["enabled"] = NotSet

    trigger.update(**updates)
    sys.stdout.write(json.dumps(trigger.to_dict()) + "\n")


def update_setup_parser(parser):
    parser.add_argument("--name", type=str, required=True, help=NAME_PARAM_HELP)
    parser.add_argument("--action-name", type=str, help=ACTION_NAME_PARAM_HELP)
    parser.add_argument(
        "--required-inputs",
        dest="required_inputs",
        type=str,
        nargs="+",
        action="extend",
        # fmt: off
        help=textwrap.dedent("""\
            One or many file patterns for data to download from the data source. Examples:
                front camera images, "--input-data '**/cam_front/*.jpg'";
                front and rear camera images, "--input-data '**/cam_front/*.jpg' --input-data '**/cam_rear/*.jpg'";
                all data, "--input-data '**/*'"
        """),
        # fmt: on
    )
    parser.add_argument(
        "--additional-inputs",
        dest="additional_inputs",
        type=str,
        nargs="+",
        action="extend",
        # fmt: off
        help=textwrap.dedent("""\
            One or many file patterns for data to download from the data source which is NOT considered as part of
            trigger evaluation. Examples:
                front camera images, "--input-data '**/cam_front/*.jpg'";
                front and rear camera images, "--input-data '**/cam_front/*.jpg' --input-data '**/cam_rear/*.jpg'";
                all data, "--input-data '**/*'"
        """),
        # fmt: on
    )
    add_org_arg(parser=parser)
    add_compute_requirements_args(parser)
    add_container_parameters_args(parser)
    parser.add_argument(
        "--condition-json",
        type=JsonFileOrStrType,
        help="Inline JSON or a reference to a JSON file "
        + "which expresses a dataset metadata and tag condition which must be met for this trigger "
        + "to run against a given dataset. If provided, 'required-tag' and 'required-metadata' cannot "
        + "be provided.",
    )
    parser.add_argument(
        "--required-tag",
        nargs="*",
        action="extend",
        help="Dataset tags which must be present for "
        + "this trigger to run against a given dataset. If provided, these are used to construct a "
        + "trigger condition, and as such they cannot be used if 'condition-json' is specified.",
    )
    parser.add_argument(
        "--required-metadata",
        nargs="*",
        action=KeyValuePairsAction,
        help="Dataset metadata "
        + "key=value conditions which all must be met for this trigger to run against a given dataset. "
        + "If provided, these are used to construct a trigger condition, and as such they cannot be "
        + "used if 'condition-json' is specified.",
    )
    parser.add_argument(
        "--for-each",
        type=TriggerForEachPrimitive,
        help="Primitive against which this trigger will spawn invocations.",
        choices=[x.value for x in TriggerForEachPrimitive],
    )
    parser.add_argument("--enabled", action="store_true", help="Enables this trigger")
    parser.add_argument("--disabled", action="store_true", help="Disables this trigger")
    parser.add_argument(
        "--clear-condition", action="store_true", help="Sets the condition to None"
    )


def get(args, context: CLIContext, parser: argparse.ArgumentParser):
    record = Trigger.from_name(
        name=args.name,
        org_id=args.org,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        trigger_delegate=context.triggers,
    )
    sys.stdout.write(json.dumps(record.to_dict()) + "\n")


def get_setup_parser(parser):
    parser.add_argument("--name", type=str, required=True, help=NAME_PARAM_HELP)
    add_org_arg(parser=parser)


def search(args, context: CLIContext, parser: argparse.ArgumentParser):
    conditions: list[Condition] = []
    if args.name:
        conditions.append(
            Condition(
                field="name",
                comparator=Comparator.Equals,
                value=args.name,
            )
        )

    if args.action_name:
        conditions.append(
            Condition(
                field="action_name",
                comparator=Comparator.Equals,
                value=args.action_name,
            )
        )

    condition = (
        None
        if len(conditions) == 0
        else ConditionGroup(
            conditions=conditions,
            operator=ConditionOperator.And,
        )
    )

    query = QuerySpecification(condition=condition)

    records = Trigger.query(
        query,
        org_id=args.org,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        trigger_delegate=context.triggers,
    )
    for record in records:
        sys.stdout.write(json.dumps(record.to_dict()) + "\n")


def search_setup_parser(parser):
    parser.add_argument(
        "--name",
        required=False,
        action="store",
        help="Query by trigger name. Must provide an exact match; patterns are not accepted.",
    )

    parser.add_argument(
        "--action-name",
        dest="action_name",
        required=False,
        action="store",
        help="Query by action name. Must provide an exact match; patterns are not accepted.",
    )

    add_org_arg(parser=parser)


def delete(args, context: CLIContext, parser: argparse.ArgumentParser):
    Trigger.from_name(
        name=args.name,
        org_id=args.org,
        action_delegate=context.actions,
        invocation_delegate=context.invocations,
        trigger_delegate=context.triggers,
    ).delete()
    sys.stdout.write("Successfully deleted!\n")


def delete_setup_parser(parser):
    parser.add_argument("--name", type=str, required=True, help=NAME_PARAM_HELP)
    add_org_arg(parser=parser)


create_command = RobotoCommand(
    name="create",
    logic=create,
    setup_parser=create_setup_parser,
    command_kwargs={
        "help": "Creates a trigger to automatically invoke some action on datasets when certain criteria are met"
    },
)

get_command = RobotoCommand(
    name="get",
    logic=get,
    setup_parser=get_setup_parser,
    command_kwargs={"help": "Looks up a specific trigger by name"},
)

delete_command = RobotoCommand(
    name="delete",
    logic=delete,
    setup_parser=delete_setup_parser,
    command_kwargs={"help": "Deletes a trigger with a given name"},
)

search_command = RobotoCommand(
    name="search",
    logic=search,
    setup_parser=search_setup_parser,
    command_kwargs={
        "help": "Searches for triggers that match a given condition. Constrained to a single org."
    },
)

update_command = RobotoCommand(
    name="update",
    logic=update,
    setup_parser=update_setup_parser,
    command_kwargs={"help": "Updates one or more fields of an existing trigger."},
)

commands = [create_command, get_command, delete_command, search_command, update_command]

command_set = RobotoCommandSet(
    name="triggers",
    help="Commands for managing triggers which automatically invoke actions on datasets when certain criteria are met",
    commands=commands,
)
