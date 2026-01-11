import type { Keyword, TokenType } from "./enums.js";


export interface I_JackTokenizer
{
    /** Are there more tokens in the input? */
    hasMoreTokens(): boolean;

    /**
     * Gets the next token from the input, and makes it the current token. This
     * method should be called only if `hasMoreTokens` is true. Initially there
     * is no current token.
     */
    advance(): void;

    /** Return the type of the current token, as a constant. */
    tokenType(): TokenType;

    /** Return the keyword which is the current token, as a constant. Should
     * only be called if `tokenType` is `KEYWORD`.
     */
    keyWord(): Keyword;

    /**
     * Return the character which is the current token. Should be called only if
     * `tokenType` is `SYMBOL`.
     */
    symbol(): string;

    /**
     * Return the string which is the current token. Should be called only if
     * `tokenType` is `IDENTIFIER`.
     */
    identifier(): string;

    /**
     * Return the integer value of the current token. Should be called only if
     * `tokenType` is `INT_CONST`.
     */
    intVal(): number;

    /**
     * Return the string value of the current token, without the opening and
     * closing double quotes. Should be called only if `tokenType` is
     * `STRING_CONST`.
     */
    stringVal(): string;
}