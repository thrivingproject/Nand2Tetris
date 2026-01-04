"""
This is the entry file to the HackAssembler.
Usage: $py HackAssembler.py <prog>.asm
Bugs: No error checking, reporting, or handling.
"""

import sys
from os import path
from parser import Parser
import coder
from symbol_table import SymbolTable


def _do_first_pass():
    """Add label symbols to symbol table."""
    parser = Parser(asm_path)
    line_no = -1  # Start at -1 so first line is 0
    while parser.has_more_lines():
        parser.advance()
        if parser.instructionType() is Parser.InstructionType.L_INSTRUCTION:
            xxx = parser.symbol()
            if symbols.contains(xxx):
                raise ValueError(f"Label symbols must be unique.")
            else:
                # Add 1 to get ROM address of next instruction
                symbols.add_symbol(xxx, line_no + 1)
        else:
            # Needed so we only add to line no for C and A instructions
            line_no += 1


def _do_second_pass():
    """Write instructions in machine language."""
    parser = Parser(asm_path)
    with open(path_root + ".hack", "w", encoding="utf-8") as f:
        while parser.has_more_lines():
            parser.advance()
            match parser.instructionType():
                case Parser.InstructionType.A_INSTRUCTION:
                    decimal_address = _get_decimal_equiv(parser.symbol())
                    line = bin(decimal_address)[2:].zfill(16)
                case Parser.InstructionType.C_INSTRUCTION:
                    comp = coder.comp(parser.comp())
                    dest = coder.dest(parser.dest())
                    jump = coder.jump(parser.jump())
                    line = f"111{comp}{dest}{jump}"
                # Skip L-Instructions
                case _:
                    continue
            f.write(line + "\n" if parser.has_more_lines() else line)


def _get_decimal_equiv(xxx: str):
    """Convert xxx to decimal address.

    If xxx is a constant, its decimal value is returned. If xxx is a symbol,
    it is added to the symbol table if necessary, and the decimal
    value it is bound to is retrieved and returned.

    Args:
        xxx: The symbol or constant in the A-instruction.
        static_address: The next available RAM address for variable symbols.
    Returns:
        int: The decimal address equivalent of xxx.
    """
    global static_address
    if xxx.isdecimal():
        # It's a constant
        address = int(xxx)
    else:
        # It's a variable symbol or label symbol
        if not symbols.contains(xxx):
            # Need to add new variable symbols to symbol table
            symbols.add_symbol(xxx, static_address)
            static_address += 1
        # Need to replace symbol with decimal value
        address = symbols.get_bound_decimal(xxx)
    return address


if __name__ == "__main__":
    asm_path = sys.argv[1]
    path_root, _ = path.splitext(asm_path)
    symbols = SymbolTable()
    static_address = 16
    _do_first_pass()
    _do_second_pass()
