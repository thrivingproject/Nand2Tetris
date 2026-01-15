export const enum TokenType {
    KEYWORD = "keyword",
    IDENTIFIER = "identifier",
    SYMBOL = "symbol",
    INT_CONST = "integer constant",
    STRING_CONST = "string constant"
}

export const ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="];

export const symbols = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", ...ops, "~"
];


export const enum Keyword {
    CLASS = "class",
    METHOD = "method",
    FUNCTION = "function",
    CONSTRUCTOR = "constructor",
    INT = "int",
    BOOLEAN = "boolean",
    CHAR = "char",
    VOID = "void",
    VAR = "var",
    STATIC = "static",
    FIELD = "field",
    LET = "let",
    DO = "do",
    IF = "if",
    ELSE = "else",
    WHILE = "while",
    RETURN = "return",
    TRUE = "true",
    FALSE = "false",
    NULL = "null",
    THIS = "this"
}

export const statementKeywords = [
    Keyword.LET,
    Keyword.IF,
    Keyword.WHILE,
    Keyword.DO,
    Keyword.RETURN,
];

export const keywords = new Map([
    ["class", Keyword.CLASS],
    ["method", Keyword.METHOD],
    ["function", Keyword.FUNCTION],
    ["constructor", Keyword.CONSTRUCTOR],
    ["int", Keyword.INT],
    ["boolean", Keyword.BOOLEAN],
    ["char", Keyword.CHAR],
    ["void", Keyword.VOID],
    ["var", Keyword.VAR],
    ["static", Keyword.STATIC],
    ["field", Keyword.FIELD],
    ["let", Keyword.LET],
    ["do", Keyword.DO],
    ["if", Keyword.IF],
    ["else", Keyword.ELSE],
    ["while", Keyword.WHILE],
    ["return", Keyword.RETURN],
    ["true", Keyword.TRUE],
    ["false", Keyword.FALSE],
    ["null", Keyword.NULL],
    ["this", Keyword.THIS]
]);