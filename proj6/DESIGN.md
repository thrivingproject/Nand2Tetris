# Hack Language Assembler

## Requirements

When given to the assembler as a command line argument, a file ending in `.asm` containing valid Hack assembly language should be translated into Hack binary code and saved to a file ending in `.hack` with the same name and in the same directory as the input file (if a file by this name exists, it is overwritten).

## Modules

### [Parser](./parser.py)

Parses the input into instructions and instructions into fields

### [Assembler](./HackAssembler.py)

Drives entire translation process

### [Coder](./coder.py)

Translates the fields into binary codes
