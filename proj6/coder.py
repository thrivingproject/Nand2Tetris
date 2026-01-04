def dest(mnemonic: str) -> str:
    """Returns binary code of the dest mnemonic

    Note we only allow certain combination orderings to match the
    online IDE even though nothing in the language specification
    or computer architecture prevents us from allowing all.
    """
    binary = ""
    match mnemonic:
        case "":
            binary += "000"
        case "M":
            binary += "001"
        case "D":
            binary += "010"
        case "DM" | "MD":
            binary += "011"
        case "A":
            binary += "100"
        case "AM":
            binary += "101"
        case "AD":
            binary += "110"
        case "ADM" | "AMD":
            binary += "111"
    return binary


def comp(mnemonic: str) -> str:
    """Returns binary code of the comp mnemonic"""
    binary = ""
    match mnemonic:
        case "0":
            binary += "0101010"
        case "1":
            binary += "0111111"
        case "-1":
            binary += "0111010"
        case "D":
            binary += "0001100"
        case "A":
            binary += "0110000"
        case "!D":
            binary += "0001101"
        case "!A":
            binary += "0110001"
        case "-D":
            binary += "0001111"
        case "-A":
            binary += "0110011"
        case "D+1":
            binary += "0011111"
        case "A+1":
            binary += "0110111"
        case "D-1":
            binary += "0001110"
        case "A-1":
            binary += "0110010"
        case "D+A":
            binary += "0000010"
        case "D-A":
            binary += "0010011"
        case "A-D":
            binary += "0000111"
        case "D&A":
            binary += "0000000"
        case "D|A":
            binary += "0010101"
        case "M":
            binary += "1110000"
        case "!M":
            binary += "1110001"
        case "-M":
            binary += "1110011"
        case "M+1":
            binary += "1110111"
        case "M-1":
            binary += "1110010"
        case "D+M":
            binary += "1000010"
        case "D-M":
            binary += "1010011"
        case "M-D":
            binary += "1000111"
        case "D&M":
            binary += "1000000"
        case "D|M":
            binary += "1010101"
    return binary


def jump(mnemonic: str) -> str:
    """Returns binary code of the jump mnemonic"""
    binary = ""
    match mnemonic:
        case "":
            binary += "000"
        case "JGT":
            binary += "001"
        case "JEQ":
            binary += "010"
        case "JGE":
            binary += "011"
        case "JLT":
            binary += "100"
        case "JNE":
            binary += "101"
        case "JLE":
            binary += "110"
        case "JMP":
            binary += "111"
    return binary
