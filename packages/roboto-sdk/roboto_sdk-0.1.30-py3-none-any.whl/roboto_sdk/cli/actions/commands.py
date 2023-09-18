#  Copyright (c) 2023 Roboto Technologies, Inc.
from ..command import RobotoCommandSet
from .create import create_command
from .delete import delete_command
from .invoke import invoke_command
from .list_invocations import (
    list_invocations_command,
)
from .search import search_command
from .show import show_command
from .update import update_command

commands = [
    create_command,
    delete_command,
    update_command,
    search_command,
    show_command,
    invoke_command,
    list_invocations_command,
]

command_set = RobotoCommandSet(
    name="actions",
    help=(
        "Create, update, delete, and query Roboto Actions. Roboto Actions can be manually invoked, "
        "or set to be triggered in response to Roboto Events."
    ),
    commands=commands,
)
