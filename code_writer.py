from typing import Literal
from command_type import CommandType
from os import path

_POP_TOP_OF_STACK_TO_D = ("@SP", "AM=M-1", "D=M")
"""Pops top of stack to D, decrements SP; destroys A register"""
_VM_TRUE = -1
_VM_FALSE = 0
_VIRTUAL_SEGMENT_POINTER = {
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
_UPDATE_FRAME_POINTER = "@R13", "AM=M-1", "D=M"
"""Decrements frame pointer, goes to register, stores value in D"""


class CodeWriter:
    """Maps VM commands to Hack machine language."""

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

    def _get_pop_asm(self, segment: str, index, pointer_to_base: None | str):
        """`pop segment index` pops the top stack value and stores it
        in segment[index].

        Args:
            segment: argument, local, static, constant, this, that, pointer, or temp.
            index: The index within the segment.
            pointer: Pointer to virtual segment base address.
        """
        lines = [f"// Pop {segment} {index}"]

        # Pop top of stack to D and select memory address to store it in
        if pointer_to_base:
            lines += [
                f"@{pointer_to_base}",
                "D=M",
                f"@{index}",
                "D=D+A",  # Calculate address of i-th entry of virtual segment
                f"@R13",
                "M=D",  # Save address to R13 since D register needed later
                *_POP_TOP_OF_STACK_TO_D,
                "@R13",
                "A=M",
            ]
        else:
            lines += [*_POP_TOP_OF_STACK_TO_D]
            if segment == "temp":
                lines.append(f"@R{5 + index}")
            elif segment == "pointer":
                lines.append("@THIS" if index == 0 else "@THAT")
            elif segment == "static":
                lines.append(f"@{self._fname}.{index}")

        # Store the value of register D in selected RAM register
        lines.append("M=D")
        return lines

    def _get_push_asm(self, segment: str, index, pointer_to_base: None | str):
        """`push segment index` pushes the value stored in a virtual register onto the stack.

        Args:
            segment: argument, local, static, constant, this, that, pointer, or temp
            index: The index within the segment.
            pointer: Pointer to virtual segment base address.
        """
        lines = [f"// Push {segment} {index}"]

        if segment == "constant":
            lines += [f"@{index}", "D=A"]
        else:
            # Select RAM register represented by virtual memory segment entry
            if segment == "temp":
                lines.append(f"@R{5 + index}")
            elif segment == "pointer":
                lines.append("@THIS" if index == 0 else "@THAT")
            elif segment == "static":
                lines.append(f"@{self._fname}.{index}")
            else:  # Local, argument, this, and that
                lines += [f"@{pointer_to_base}", "D=M", f"@{index}", "A=D+A"]
            # Set D register to selected RAM register's value
            lines.append("D=M")

        # Push D to top of stack
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
                *_POP_TOP_OF_STACK_TO_D,
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

    def close(self) -> None:
        """Close the output file."""
        self._out.close()

    def set_file_name(self, fname: str) -> None:
        """Inform that the translation of a new VM file has started."""
        ...

    def write_arithmetic(self, command: str) -> None:
        """Write to the output file the assembly code that implements
        the given arithmetic-logical command.

        For neg and not, one operand is popped off the stack.
        Otherwise, two operands are popped. The computed value is
        pushed onto the stack.

        Args:
            command: The arithmetic-logical command to be performed.
        """
        lines = [f"// {command}"]
        if command in ("gt", "lt", "eq"):
            lines += self._write_comparison_command(command)
        else:
            lines += [*_POP_TOP_OF_STACK_TO_D]
            if command in ("add", "sub", "and", "or"):
                lines.append("A=A-1")  # Needed to access second operand
                lines.append(_ARITHMETIC_ASM_MAP[command])
            else:
                lines.append("M=-D" if command == "neg" else "M=!D")
                lines += ["@SP", "M=M+1"]
        self._writelines(lines)

    def write_call(self, fn_name: str, n_vars: int) -> None:
        """Write assembly code that implements the call command.

        `call fn_name n_args` calls the named function. The command informs that n_vars arguments have pushed onto the stack before the call.
        """
        lines = [f"// call {fn_name} {n_vars}"]
        self._writelines(lines)

    def write_function(self, fn_name: str, n_vars: int) -> None:
        """Write assembly code that implements the function command.

        `function fn_name n_vars` marks the beginning of a function named fn_name. The command informs that the function has n_vars local variables.
        """
        lines = [f"// function {fn_name} {n_vars}", f"({fn_name})"]
        # Push 0 to stack for each local variable
        if n_vars:
            lines += ["@SP", "A=M", "M=0"]
            lines += ("A=A+1", "M=0") * (n_vars - 1)
            lines.append("@SP")
            lines += ("M=M+1",) * n_vars

        self._writelines(lines)

    def write_goto(self, label: str) -> None:
        """Write assembly code that implements the goto command."""
        self._writelines([f"// goto {label}", f"@{label}", "0;JMP"])

    def write_if(self, label: str) -> None:
        """Write assembly code that implements the if-goto command.

        The stack's topmost value is popped; if the value is not zero (false), i.e., if the value is true, execution continues from the location marked by the label; otherwise, execution continues from the next command in the program.
        """
        lines = [
            f"// if-goto {label}",
            *_POP_TOP_OF_STACK_TO_D,
            f"@{label}",
            "D;JNE",  # Jump if D is not 0 (is not false)
        ]
        self._writelines(lines)

    def write_label(self, label: str) -> None:
        """Write assembly code that implements the label command."""
        self._writelines([f"// label {label}", f"({label})"])

    def write_push_pop(
        self,
        command: Literal[CommandType.C_POP, CommandType.C_PUSH],
        segment: str,
        index: int,
    ) -> None:
        """Write to the output file the assembly code that implements the push/pop command."""
        pointer = _VIRTUAL_SEGMENT_POINTER.get(segment)
        if command == CommandType.C_PUSH:
            lines = self._get_push_asm(segment, index, pointer)
        else:
            lines = self._get_pop_asm(segment, index, pointer)
        self._writelines(lines)

    def write_return(self) -> None:
        """Write assembly code that implements the return command.

        `return` transfers execution to the command just following the call command in the code of the function that called the current function.
        """
        lines = [
            f"// return",
            "@LCL",
            "D=M-1",
            "@R13",  # Pointer to last register of stack frame
            "M=D",  # Store address of stack frame in R13
            *_POP_TOP_OF_STACK_TO_D,
            "@ARG",
            "A=M",
            "M=D",  # Put callee's return value on top of caller's stack
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",  # Reposition SP for the caller
            "@R13",
            "A=M",  # Select last register of stack frame
            "D=M",
            "@THAT",
            "M=D",  # Restore THAT for caller
            *_UPDATE_FRAME_POINTER,
            "@THIS",
            "M=D",  # Restore THIS for caller
            *_UPDATE_FRAME_POINTER,
            "@ARG",
            "M=D",  # Restore ARG for caller
            *_UPDATE_FRAME_POINTER,
            "@LCL",
            "M=D",  # Restore LCL for caller
            "@R13",
            "A=M-1",
            "0;JMP",  # go to the return address
        ]
        self._writelines(lines)
