from typing import Literal
from command_type import CommandType
from os import path

_POP_STACK_TOP_TO_D = ("@SP", "AM=M-1", "D=M")
_PUSH_D_TO_STACK = ("@SP", "A=M", "M=D", "@SP", "M=M+1")
_VM_TRUE = -1
_VM_FALSE = 0


class CodeWriter:
    """Translate a parsed VM command into Hack assembly."""

    def __init__(self, fpath: str) -> None:
        """Open output file and gets read to write into it.

        Args:
            fpath: path to VM file
        """
        root, _ = path.splitext(fpath)
        self._fname = path.basename(root)
        self._f = open(f"{root}.asm", "w")
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
        lines = [f"// {command}", *_POP_STACK_TOP_TO_D]
        match command:
            case "add" | "sub" | "eq" | "gt" | "lt" | "and" | "or":
                lines += [
                    "@R14",
                    "M=D",
                    *_POP_STACK_TOP_TO_D,
                    "@R14",
                ]
                if command == "add":
                    lines.append("D=D+M")
                elif command == "sub":
                    lines.append("D=D-M")
                elif command == "and":
                    lines.append("D=D&M")
                elif command == "or":
                    lines.append("D=D|M")
                else:
                    op = command.upper()
                    op_label_num = self._label_d.setdefault(op, 0)
                    self._label_d[op] += 1
                    lines += [
                        "D=D-M",
                        f"@{op}_TRUE.{op_label_num}",
                        f"D;J{op}",
                        f"D={_VM_FALSE}",
                        f"@{op}_END.{op_label_num}",
                        "0;JMP",
                        f"({op}_TRUE.{op_label_num})",
                        f"D={_VM_TRUE}",
                        f"({op}_END.{op_label_num})",
                    ]
            case "neg" | "not":
                lines.append(f"D={'-' if command == 'neg' else '!'}D")
            case _:
                raise ValueError(f"Bad write_arithmetic command: {command}")
        lines += [*_PUSH_D_TO_STACK]
        self._add_newline_and_writelines(lines)

    def write_push_pop(
        self,
        command: Literal[CommandType.C_POP, CommandType.C_PUSH],
        segment: str,
        index: int,
    ) -> None:
        """Write to the output file the assembly code that implements the push/pop command.

        `push` pushes the value of segment[index] onto the stack.
        `pop` pops the top stack value and stores it in segment[index].

        Args:
            command: The command type, either C_PUSH or C_POP.
            segment: argument, local, static, constant, this, that, pointer, or temp
            index: The index within the segment.
        """
        base, ptr = self._get_symbols(segment, index)
        match command:
            case CommandType.C_PUSH:
                lines = [f"// Push {segment} {index}"]
                if segment in ("local", "argument", "this", "that"):
                    lines += [f"@{base}", "D=M", f"@{index}", "A=D+A"]
                else:
                    lines += [f"@{ptr}"]
                lines += [
                    f"D={'A' if segment == 'constant' else 'M'}",
                    *_PUSH_D_TO_STACK,
                ]
            case CommandType.C_POP:
                if segment == "constant":
                    raise ValueError("Cannot pop to constant segment")
                lines = [f"// Pop {segment} {index}"]
                # Calculate address and save it to move top of stack to later
                if segment in ("local", "argument", "this", "that"):
                    lines += [
                        f"@{base}",
                        "D=M",
                        f"@{index}",
                        "D=D+A",
                        f"@{ptr}",
                        "M=D",
                    ]
                # Pop top of stack to D so we can write D to the address
                lines += [*_POP_STACK_TOP_TO_D]
                # Get the address so we can write D to it
                lines.append(f"@{ptr}")
                if segment in ("local", "argument", "this", "that"):
                    lines.append("A=M")
                lines.append("M=D")
            case _:
                raise ValueError(f"Bad write_push_pop command: {command}")
        self._add_newline_and_writelines(lines)

    def close(self) -> None:
        """Close the output file."""
        self._f.close()

    def _add_newline_and_writelines(self, lines: list[str]):
        """Add newline character to end of each line and write lines to file."""
        lines = [line + "\n" for line in lines]
        self._f.writelines(lines)

    def _get_symbols(self, segment: str, index: int) -> tuple[str, str]:
        """Return the symbols for pointers to virtual registers.

        Args:
            segment: virtual memory segment
            index: The index within the segment.

        Returns:
            (base, ptr): tuple containing symbol for pointer to first address of the virtual memory segment,
            and symbol for pointer to the address corresponding to segment[index].
        """
        match segment:
            case "local" | "argument" | "this" | "that":
                if segment == "local":
                    base = "LCL"
                elif segment == "this":
                    base = "THIS"
                elif segment == "that":
                    base = "THAT"
                else:
                    base = "ARG"
                return base, "R13"
            case "static":
                return "", f"{self._fname}.{index}"
            case "constant":
                return "", f"{index}"
            case "temp":
                return "", f"R{5 + index}"
            case "pointer":
                return "", "THIS" if index == 0 else "THAT"
            case _:
                raise ValueError(f"Bad segment: {segment}")
