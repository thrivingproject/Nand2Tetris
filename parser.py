from enum import Enum


class Parser:
    """Parses the input into instructions and instructions into fields"""

    class InstructionType(Enum):
        A_INSTRUCTION = 1
        C_INSTRUCTION = 2
        L_INSTRUCTION = 3

    _lines: list[str]
    _index: int
    _current_instruction: str

    def __init__(self, asm_path) -> None:
        self._index = -1
        self._lines = []
        with open(asm_path, "rt", encoding="utf-8") as f:
            for line in f:
                # strip() needed so lines indentions are removed
                self._lines.append(line.strip())

    def has_more_lines(self) -> bool:
        """Are there more lines in the assembly file to parse?"""
        return self._index + 1 < len(self._lines)

    def advance(self) -> None:
        """Advance to the next valid instruction, skipping comments and blank lines"""
        self._index += 1
        self._current_instruction = self._lines[self._index]
        if (
            self._current_instruction.startswith("//")
            # Check for "" since strip() turns lines with just "\n" into ""
            or self._current_instruction == ""
        ) and self.has_more_lines():
            self.advance()

    def instructionType(self) -> InstructionType:
        """Return the type of currently selected instruction"""
        if self._current_instruction.startswith("@"):
            return self.InstructionType.A_INSTRUCTION
        elif self._current_instruction.startswith("("):
            return self.InstructionType.L_INSTRUCTION
        else:
            return self.InstructionType.C_INSTRUCTION

    def symbol(self) -> str:
        """Returns symbol for L-Instructions and A-Instructions"""
        return self._current_instruction[1:]

    def dest(self) -> str:
        """Returns the symbolic _dest_ part of the current C-Instruction"""
        eq_sign = self._current_instruction.find("=")
        # Need to end at 0 so we get empty string if = not found
        end = 0 if eq_sign == -1 else eq_sign
        return self._current_instruction[:end]

    def comp(self) -> str:
        """Returns the symbolic _comp_ part of the current C-Instruction"""
        jump_sep = self._current_instruction.find(";")
        # Needed since -1 doesn't include last character and None does
        end = None if jump_sep == -1 else jump_sep
        return self._current_instruction[
            # Add 1 to start at 0 if no '=' and to skip '=' if found
            (self._current_instruction.find("=") + 1) : end
        ]

    def jump(self) -> str:
        """Returns the symbolic _jump_ part of the current C-Instruction"""
        jump_sep = self._current_instruction.find(";")
        if jump_sep == -1:
            return ""
        return self._current_instruction[jump_sep + 1 :]
