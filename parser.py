from command_type import CommandType


class Parser:
    """Parses Hack VM commands."""

    def __init__(self, fpath) -> None:
        """Open the input file and prepare to parse it.

        Args:
            fpath: path to VM file
        """
        with open(fpath, "r") as f:
            self._lines = f.readlines()
            self._line_ndx = -1

    def has_more_lines(self) -> bool:
        """Return true if there are more commands in the input, else false."""
        return self._line_ndx < len(self._lines) - 1

    def advance(self) -> None:
        """Read the command from the input and make it the current command.

        Should only be called if `has_more_lines` is `True`. Initially there is no current command.
        """
        self._line_ndx += 1
        cur_line = self._lines[self._line_ndx].strip()
        if (
            not cur_line or cur_line.startswith(("//", "\n"))
        ) and self.has_more_lines():
            self.advance()

    def command_type(self) -> CommandType:
        """Return a constant representing the type of the current command."""
        match self._get_command_items()[0]:
            case (
                "add"
                | "sub"
                | "neg"
                | "eq"
                | "gt"
                | "lt"
                | "and"
                | "or"
                | "not"
            ):
                return CommandType.C_ARITHMETIC
            case "push":
                return CommandType.C_PUSH
            case "pop":
                return CommandType.C_POP
            case "call":
                return CommandType.C_CALL
            case "goto":
                return CommandType.C_GOTO
            case "if-goto":
                return CommandType.C_IF
            case "function":
                return CommandType.C_FUNCTION
            case "label":
                return CommandType.C_LABEL
            case "return":
                return CommandType.C_RETURN
            case _:
                raise ValueError("Unknown command type")

    def arg_1(self) -> str:
        """Return the first argument of the current command.

        In the case of C_ARITHMETIC the command itself (add, sub, etc.) is returned. Should not be called if the current command is C_RETURN.
        """
        if self.command_type() == CommandType.C_RETURN:
            raise ValueError("arg_1 called on C_RETURN command")
        items = self._get_command_items()
        if self.command_type() == CommandType.C_ARITHMETIC:
            return items[0]
        else:
            return items[1]

    def arg_2(self) -> int:
        """Return the second argument of the current command.

        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or, C_CALL.
        """
        if self.command_type() not in {
            CommandType.C_PUSH,
            CommandType.C_POP,
            CommandType.C_FUNCTION,
            CommandType.C_CALL,
        }:
            raise ValueError("arg_2 called on invalid command type")
        items = self._get_command_items()
        return int(items[2])

    def _get_command_items(self) -> list[str]:
        """Return the current command split into its items."""
        return self._lines[self._line_ndx].split()
