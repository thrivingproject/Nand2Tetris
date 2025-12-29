import sys
from parser import Parser
from code_writer import CodeWriter
from command_type import CommandType

vm_path = sys.argv[1]
parser = Parser(vm_path)
cw = CodeWriter(vm_path)

while parser.has_more_lines():
    parser.advance()
    command = parser.command_type()
    match command:
        case CommandType.C_ARITHMETIC:
            cw.write_arithmetic(parser.arg_1())
        case CommandType.C_CALL:
            ...
        case CommandType.C_FUNCTION:
            ...
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
