export const enum TokenType {
    KEYWORD, IDENTIFIER, SYMBOL, INT_CONST, STRING_CONST
}

export const symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-",
    "*", "/", "&", "|", "<", ">", "=", "~"];


export const enum Keyword {
    CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC,
    FIELD, LET, DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS
}

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