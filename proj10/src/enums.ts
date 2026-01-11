export const enum TokenType
{
    KEYWORD, IDENTIFIER, SYMBOL, INT_CONST, STRING_CONST
}

export const keywords = ["class", "method", "function", "constructor", "int",
    "boolean", "char", "void", "var", "static", "field", "let", "do", "if",
    "else", "while", "return", "true", "false", "null", "this"];

export const symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-",
    "*", "/", "&", "|", "<", ">", "=", "~"];


export const enum Keyword
{
    CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC,
    FIELD, LET, DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS
}