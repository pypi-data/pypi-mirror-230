#  Copyright (c) 2023 Roboto Technologies, Inc.
from ..command import RobotoCommandSet
from .logs import get_logs_command
from .show import show_command
from .status import status_command

commands = [
    get_logs_command,
    show_command,
    status_command,
]

command_set = RobotoCommandSet(
    name="invocations",
    help=("Show details of action invocations, their status history, and logs."),
    commands=commands,
)
