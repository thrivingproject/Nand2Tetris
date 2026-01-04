import sys
from parser import Parser
from code_writer import CodeWriter
from command_type import CommandType
from pathlib import Path

source = Path(sys.argv[1])
parsers: dict[str, Parser] = {}

if source.is_file():
    parsers[source.stem] = Parser(source)
elif source.is_dir():
    for child in source.iterdir():
        if child.suffix == ".vm":
            parsers[child.stem] = Parser(child)
else:
    raise ValueError("Input path is neither a file nor a directory")

cw = CodeWriter(source)
for fname, parser in parsers.items():
    cw.set_file_name(fname)
    while parser.has_more_lines():
        parser.advance()
        command = parser.command_type()
        match command:
            case CommandType.C_ARITHMETIC:
                cw.write_arithmetic(parser.arg_1())
            case CommandType.C_CALL:
                cw.write_call(parser.arg_1(), parser.arg_2())
            case CommandType.C_FUNCTION:
                cw.write_function(parser.arg_1(), parser.arg_2())
            case CommandType.C_GOTO:
                cw.write_goto(parser.arg_1())
            case CommandType.C_IF:
                cw.write_if(parser.arg_1())
            case CommandType.C_LABEL:
                cw.write_label(parser.arg_1())
            case CommandType.C_PUSH | CommandType.C_POP:
                cw.write_push_pop(command, parser.arg_1(), parser.arg_2())
            case CommandType.C_RETURN:
                cw.write_return()
cw.close()
