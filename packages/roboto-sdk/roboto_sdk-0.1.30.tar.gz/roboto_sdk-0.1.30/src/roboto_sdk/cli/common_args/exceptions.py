import typing


class ParseError(Exception):
    msg: typing.Any

    def __init__(self, msg, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg
