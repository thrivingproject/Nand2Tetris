"""
This module drives translation process.
Assumes source assembly contains no symbolic references.
Bugs: No error checking, reporting, or handling.
"""

import sys
from os import path

from parser import Parser
import coder

asm_path = sys.argv[1]
path_root, _ = path.splitext(asm_path)
hack_path = path_root + ".hack"

parser = Parser(asm_path)

with open(hack_path, "w", encoding="utf-8") as f:
    while parser.has_more_lines():
        parser.advance()
        line = ""

        match parser.instructionType():
            case Parser.InstructionType.A_INSTRUCTION:
                # Need to cast to int since bin accepts int
                translation = bin(int(parser.symbol()))[2:]  # Cut off '0b'
                # Pad with zeros since bin uses as fewest bits as is possible
                line += translation.zfill(16)
            case Parser.InstructionType.C_INSTRUCTION:
                line += (
                    "111"
                    + coder.comp(parser.comp())
                    + coder.dest(parser.dest())
                    + coder.jump(parser.jump())
                )

        f.write(line + "\n" if parser.has_more_lines() else line)
