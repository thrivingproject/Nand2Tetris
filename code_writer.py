from typing import Literal
from command_type import CommandType
from os import path

_POP_TO_D = ("@SP", "AM=M-1", "D=M")
_VM_TRUE = -1
_VM_FALSE = 0
_SEGMENT_LABEL_MAP = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}


class CodeWriter:
    """Translate a parsed VM command into Hack assembly."""

    def __init__(self, fpath: str) -> None:
        """Open output file and gets read to write into it.

        Args:
            fpath: path to VM file
        """
        root, _ = path.splitext(fpath)
        self._fname = path.basename(root)
        self._out = open(f"{root}.asm", "w")
        self._label_d: dict[str, int] = {}

    def set_file_name(self, fname: str) -> None:
        """Inform that the translation of a new VM file has started."""
        ...

    def write_label(self, label: str) -> None:
        """Write assembly code that implements the label command."""
        ...

    def write_goto(self, label: str) -> None:
        """Write assembly code that implements the goto command."""
        ...

    def write_if(self, label: str) -> None:
        """Write assembly code that implements the if-goto command."""
        ...

    def write_function(self, fn_name: str, n_vars: int) -> None:
        """Write assembly code that implements the function command."""
        ...

    def write_call(self, fn_name: str, n_vars: int) -> None:
        """Write assembly code that implements the call command."""
        ...

    def write_return(self) -> None:
        """Write assembly code that implements the return command."""
        ...

    def write_arithmetic(self, command: str) -> None:
        """Write to the output file the assembly code that implements the given arithmetic-logical command.

        For neg and not, one operand is popped off the stack; `operator operand` is computed.
        Otherwise, two operands are popped; `operand1 operator operand2` is computed.
        The computed value is pushed onto the stack.

        Args:
            command: The arithmetic-logical command to be performed.
        """
        lines = [f"// {command}", *_POP_TO_D]
        match command:
            case "neg" | "not":
                lines += [
                    f"M={'-' if command == 'neg' else '!'}D",
                    "@SP",
                    "M=M+1",
                ]
            case "add" | "sub" | "and" | "or" | "eq" | "gt" | "lt":
                lines.append("A=A-1")  # Get second arg
                if command == "add":
                    lines.append("M=D+M")
                elif command == "sub":
                    lines.append("M=M-D")
                elif command == "and":
                    lines.append("M=D&M")
                elif command == "or":
                    lines.append("M=D|M")
                else:
                    comparison = command.upper()
                    count = self._label_d.setdefault(comparison, 0)
                    self._label_d[comparison] += 1
                    lines += [
                        "D=M-D",
                        # Assume comparison true
                        f"M={_VM_TRUE}",
                        f"@{comparison}_END.{count}",
                        f"D;J{comparison}",
                        # Correct M if not true
                        "@SP",
                        "A=M-1",
                        f"M={_VM_FALSE}",
                        f"({comparison}_END.{count})",
                    ]
            case _:
                raise ValueError(f"Bad write_arithmetic command: {command}")
        self._add_newline_and_writelines(lines)

    def write_push_pop(
        self,
        command: Literal[CommandType.C_POP, CommandType.C_PUSH],
        segment: str,
        index: int,
    ) -> None:
        """Write to the output file the assembly code that implements the push/pop command."""
        if command == CommandType.C_PUSH:
            lines = self._write_push(segment, index)
        else:
            lines = self._write_pop(segment, index)
        self._add_newline_and_writelines(lines)

    def _write_pop(self, segment, index):
        """Write to the output file the assembly code that implements the pop command.

        `pop segment index` pops the top stack value and stores it in segment[index].

        Args:
            segment: argument, local, static, constant, this, that, pointer, or temp
            index: The index within the segment.
        """
        if segment == "constant":
            raise ValueError("Cannot pop to constant segment")
        lines = [f"// Pop {segment} {index}"]
        if segment in ("local", "argument", "this", "that"):
            lines += [
                f"@{_SEGMENT_LABEL_MAP[segment]}",
                "D=M",
                f"@{index}",
                "D=D+A",
                f"@R13",
                "M=D",
                [*_POP_TO_D],
                "@R13",
                "A=M",
            ]
        else:
            lines += [*_POP_TO_D]
            # Append assemble line to select memory register
            if segment == "temp":
                lines.append(f"@R{5 + index}")
            elif segment == "pointer":
                lines.append("@THIS" if index == 0 else "@THAT")
            elif segment == "static":
                lines.append(f"@{self._fname}.{index}")
        lines.append("M=D")
        return lines

    def _write_push(self, segment, index):
        """Write to the output file the assembly code that implements the push command.

        `push segment index` pushes the value of segment[index] onto the stack.

        Args:
            segment: argument, local, static, constant, this, that, pointer, or temp
            index: The index within the segment.
        """
        lines = [f"// Push {segment} {index}"]
        # Select memory register / store constant value in A register
        if segment in ("local", "argument", "this", "that"):
            lines += [
                f"@{_SEGMENT_LABEL_MAP[segment]}",
                "D=M",
                f"@{index}",
                "A=D+A",
            ]
        elif segment == "temp":
            lines.append(f"@R{5 + index}")
        elif segment == "pointer":
            lines.append("@THIS" if index == 0 else "@THAT")
        elif segment == "static":
            lines.append(f"@{self._fname}.{index}")
        else:
            lines.append(f"@{index}")
        # Store value in memory register / constant in D register
        lines.append(f"D={'A' if segment == 'constant' else 'M'}")
        # Push D to stack top
        lines += ["@SP", "AM=M+1", "A=A-1", "M=D"]
        return lines

    def close(self) -> None:
        """Close the output file."""
        self._out.close()

    def _add_newline_and_writelines(self, lines: list[str]):
        """Add newline character to end of each line and write lines to file."""
        lines = [line + "\n" for line in lines]
        self._out.writelines(lines)
