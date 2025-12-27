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
_ARITHMETIC_ASM_MAP = {
    "add": "M=D+M",
    "sub": "M=M-D",
    "and": "M=D&M",
    "or": "M=D|M",
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
        self._writelines(["@START", "0;JMP"])
        self._write_reusable_comparisons()
        self._writelines(["(START)"])

    def _writelines(self, lines: list[str]):
        """Add newline character to end of each line and write lines to file."""
        for line in lines:
            self._out.write(line + "\n")

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
                *_POP_TO_D,
                "@R13",
                "A=M",
            ]
        else:
            lines += [*_POP_TO_D]
            # Append assembly line to select memory register
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

    def _write_reusable_comparisons(self):
        """Write assembly for eq, lt, gt operations.

        This allows the code to be reusable such that each time the operation
        is needs performed, all that the "caller" needs to do is create a
        label symbol with return address, save it to D register, and jump here.
        """
        for operator in ("EQ", "LT", "GT"):
            lines = [
                f"({operator}_START)",
                # Save return address
                "@R14",
                "M=D",
                *_POP_TO_D,
                # Calculate and push to stack
                "A=A-1",
                "D=M-D",
                f"M={_VM_TRUE}",
                f"@{operator}_END",
                f"D;J{operator}",
                "@SP",
                "A=M-1",
                f"M={_VM_FALSE}",
                f"({operator}_END)",
                # Load return address and jump
                "@R14",
                "A=M",
                "0;JMP",
            ]
            self._writelines(lines)

    def _write_comparison_command(self, command: str):
        """Write assembly code to effect comparison commands.

        A label symbol is created to indicate the address where execution
        should resume after the comparison result is pushed onto the stack.
        The same symbol is used as a variable to set the A register to the
        return address, which is then stored in the D register. Control
        then jumps to the reusable comparison assembly.
        """
        operator = command.upper()
        num = self._label_d.setdefault(operator, 0)
        self._label_d[operator] += 1
        return_address_symbol = f"RET_ADDRESS_{operator}{num}"
        return [
            f"@{return_address_symbol}",
            "D=A",
            f"@{operator}_START",
            "0;JMP",
            f"({return_address_symbol})",
        ]

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
        lines = [f"// {command}"]
        if command in ("gt", "lt", "eq"):
            lines += self._write_comparison_command(command)
        else:
            lines += [*_POP_TO_D]
            if command in ("add", "sub", "and", "or"):
                lines.append("A=A-1")  # Needed to access second operand
                lines.append(_ARITHMETIC_ASM_MAP[command])
            else:
                lines.append("M=-D" if command == "neg" else "M=!D")
                lines += ["@SP", "M=M+1"]
        self._writelines(lines)

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
        self._writelines(lines)

    def close(self) -> None:
        """Close the output file."""
        self._out.close()
