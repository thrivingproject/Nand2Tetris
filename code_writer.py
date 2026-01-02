from pathlib import Path
from typing import Literal
from command_type import CommandType

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
_PUSH_D_TO_STACK = "@SP", "AM=M+1", "A=A-1", "M=D"
"""Push D to top of stack and increments SP; destroys A"""


class CodeWriter:
    """Maps VM commands to Hack machine language."""

    def __init__(self, fpath: Path) -> None:
        """Open output file and gets read to write into it.

        Args:
            fpath: path to a single vm file or a folder containing VM files
        """
        parent = fpath.parent if fpath.is_file() else fpath
        self._label_d: dict[str, int] = {}
        """Used to track unique labels for comparison commands."""
        self._vm_fname: str
        """Needed to add VM filename to labels and static variables."""
        self._function: str
        """Used for label symbols."""
        self._out = open(f"{parent}/{fpath.stem}.asm", "w")
        self._bootstrap()

    def _bootstrap(self):
        """Write initial assembly."""
        self._function = ""
        self._writelines(["// Bootstrap", "@256", "D=A", "@SP", "M=D"])
        self.write_call("Sys.init", 0)
        self._writelines(self._get_reusable_comparisons())
        self._writelines(self._get_reusable_write_call())

    def _writelines(self, lines: list[str]):
        """Add newline character to end of each line and write lines to file."""
        for line in lines:
            if not line.startswith(
                (
                    "// function",
                    "// Bootstrap",
                    "// Comparisons",
                    "// Call reusable snippet",
                )
            ):
                self._out.write("\t" + line + "\n")
            else:
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
                lines.append(f"@{self._vm_fname}.{index}")

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
                lines.append(f"@{self._vm_fname}.{index}")
            else:  # Local, argument, this, and that
                lines += [f"@{pointer_to_base}", "D=M", f"@{index}", "A=D+A"]
            # Set D register to selected RAM register's value
            lines.append("D=M")

        # Push D to top of stack
        lines += [*_PUSH_D_TO_STACK]
        return lines

    def _get_fn_return_label_symbol(self):
        """Return `functionName$ret.i` and update label dictionary with current value of i."""
        ret_label_prefix = f"{self._function}$ret."
        i = self._label_d.setdefault(ret_label_prefix, 0)
        self._label_d[ret_label_prefix] += 1
        return ret_label_prefix + str(i)

    def _get_ret_address_label_symbol(self, computation: str) -> str:
        """Return a label symbol used when performing reusable assembly functionality.

        The label is used to store the return address and inject the return label when before jumping to reusable comparisons, function call, and function return assembly.
        """
        n = self._label_d.setdefault(computation, 0)
        self._label_d[computation] += 1
        return f"RET_ADDRESS_{computation}{n}"

    def _get_reusable_comparisons(self):
        """Return assembly for eq, lt, gt operations.

        This allows the code to be reusable such that each time the operation
        is needs performed, all that the "caller" needs to do is create a
        label symbol with return address, save it to D register, and jump here.
        """
        lines: list[str] = ["// Comparisons"]
        for operator in ("EQ", "LT", "GT"):
            lines += [
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
        return lines

    def _get_reusable_write_call(self) -> list[str]:
        """Return assembly of reusable write call snippet.

        Snippet expects following:
        - nArgs pushed stored in R13
        - callee address stored in R14
        - caller return address is stored in D
        """
        return [
            "// Call reusable snippet",
            "(CALL_START)",
            *_PUSH_D_TO_STACK,  # Push return address
            "@LCL",
            "D=M",
            *_PUSH_D_TO_STACK,  # Push caller's LCL onto stack
            "@ARG",
            "D=M",
            *_PUSH_D_TO_STACK,  # Push caller's ARG onto stack
            "@THIS",
            "D=M",
            *_PUSH_D_TO_STACK,  # Push caller's THIS onto stack
            "@THAT",
            "D=M",
            *_PUSH_D_TO_STACK,  # Push caller's THAT onto stack
            "@5",
            "D=A",
            "@R13",
            "D=D+M",
            "@SP",
            "D=M-D",
            "@ARG",
            "M=D",  # Update ARG for callee function
            "@SP",
            "D=M",
            "@LCL",
            "M=D",  # Update LCL for callee function
            "@R14",
            "A=M",
            "0;JMP",  # Jump to callee
        ]

    def _write_comparison_command(self, command: str):
        """Write assembly code to effect comparison commands.

        A label symbol is created to indicate the address where execution
        should resume after the comparison result is pushed onto the stack.
        The same symbol is used as a variable to set the A register to the
        return address, which is then stored in the D register. Control
        then jumps to the reusable comparison assembly.
        """
        operator = command.upper()
        return_address_symbol = self._get_ret_address_label_symbol(operator)
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
        self._vm_fname = fname

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

    def write_call(self, fn_name: str, n_args: int) -> None:
        """Write assembly code that implements the call command.

        `call fn_name n_args` calls fn_name. The command informs that n_args arguments have pushed onto the stack before the call.

        Args:
            fn_name: The label for the callee.
            n_args: The number of arguments pushed onto the stack.
        """
        return_label_symbol = self._get_fn_return_label_symbol()
        lines = [
            f"// call {fn_name} {n_args}",
            f"@{n_args}",
            "D=A",
            "@R13",
            "M=D",  # Store nArgs in R13
            f"@{fn_name}",
            "D=A",
            "@R14",
            "M=D",  # Store callee address in R14
            f"@{return_label_symbol}",
            "D=A",
            "@CALL_START",
            "0;JMP",  # Jump to reusable call assembly
            f"({return_label_symbol})",
        ]
        self._writelines(lines)

    def write_function(self, fn_name: str, n_vars: int) -> None:
        """Write assembly code that implements the function command.

        `function fn_name n_vars` marks the beginning of a function named fn_name. The command informs that the function has n_vars local variables.

        Args:
            fn_name: The name of the function being written.
            n_vars: The number of local variables the function has.
        """
        self._function = fn_name
        lines = [f"// function {fn_name} {n_vars}", f"({fn_name})"]
        # Push 0 to stack for each local variable
        if n_vars:
            lines += ["@SP", "A=M", "M=0"]
            for _ in range(n_vars - 1):
                lines += ["@SP", "AM=M+1", "M=0"]
            lines += ["@SP", "M=M+1"]

        self._writelines(lines)

    def write_goto(self, label: str) -> None:
        """Write assembly code that implements the goto command.

        `goto label` causes an unconditional jump. The goto command and the labeled jump destination must be in the same function.
        """
        self._writelines(
            [f"// goto {label}", f"@{self._function}${label}", "0;JMP"]
        )

    def write_if(self, label: str) -> None:
        """Write assembly code that implements the if-goto command.

        The stack's topmost value is popped; if the value is false, i.e., if the value is anything other than zero, execution continues from the location marked by the label; otherwise, if the value is zero, execution continues from the next command in the program. The if-goto command and the labeled jump destination must be in the same function.
        """
        lines = [
            f"// if-goto {label}",
            *_POP_TOP_OF_STACK_TO_D,
            f"@{self._function}${label}",
            "D;JNE",  # Jump if D is true
        ]
        self._writelines(lines)

    def write_label(self, label: str) -> None:
        """Write assembly code that implements the label command.

        `label label` Labels the current location in the function's code. The scope of the label is the function in which it is defined.
        """
        self._writelines([f"// label {label}", f"({self._function}${label})"])

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
            "@R13",
            "M=D",  # Store pointer to end of caller's stack frame in R13
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
            "A=M-1",  # Select register containing pointer to return address
            "A=M",  # Select return address
            "0;JMP",  # Jump to the return address
        ]
        self._writelines(lines)
