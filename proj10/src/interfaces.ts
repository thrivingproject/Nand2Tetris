import type { Keyword, TokenType } from "./enums.js";


export interface I_JackTokenizer {
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
    /**
     * Return the keyword which is the current token, as a constant. Should
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

export interface I_CompilationEngine {
    /**
     * Compiles a complete class:
     * 
     * '**class**' className '**{**' classVarDec* subroutineDec* '**}**'
     */
    compileClass(): void;
    /**
     * Compiles a static variable declaration:
     * 
     * ('**static**' | '**field**') type varName (',' varName)* ';'
     */
    compileClassVarDec(): void;
    /**
     * Compiles a complete method, function, or constructor declaration:
     * 
     * ('**constructor**' | '**function**' | '**method**') ('**void**' | type)
     * subroutineName '**(**' parameterList '**)**' subroutineBody
     */
    compileSubroutineDec(): void;
    /**
     * Compiles a (possibly empty) parameter list. Does not handle the enclosing
     * parentheses tokens `(` and `)`:
     * 
     * ((type varName) (',' type varName)*)?
     */
    compileParameterList(): void;
    /**
     * Compiles a subroutine's body:
     * 
     * '**{**' varDec* statements '**}**'
     */
    compileSubroutineBody(): void;
    /**
     * Compiles a `var` declaration:
     * 
     * '**var**' type varName (',' varName)*';'
     */
    compileVarDec(): void;
    /**
     * Compiles a sequence of statements. Does not handle the enclosing brackets
     * `{` and `}`:
     * 
     * statement*
     * 
     * where statement is: 
     * 
     * letStatement | ifStatement | whileStatement | doStatement |
     * returnStatement
     */
    compileStatements(): void;
    /**
     * Compiles a `let` statement:
     * 
     * '**let**' varName ('[' expression ']')? '=' expression ';'
     */
    compileLet(): void;
    /**
     * Compiles a `if` statement:
     * 
     * '**if**' '**(**' expression '**)**' '**{**' statements '**}**' ('**else**' '**{**' statements '**}**')? 
     */
    compileIf(): void;
    /**
     * Compiles a `while` statement:
     * 
     * '**while**' '**(**' expression '**)**' '**{**' statements '**}**'
     */
    compileWhile(): void;
    /**
     * Compiles a `do` statement:
     * 
     * '**do**' subroutineCall ';'
     */
    compileDo(): void;
    /**
     * Compiles a `return` statement:
     * 
     * '**return**' expression? ';'
     */
    compileReturn(): void;
    /**
     * Compiles an expression:
     * 
     * term (op term)*
     */
    compileExpression(): void;
    /**
     * Compiles a *term*. If the current token is an *identifier*, the routine
     * must resolve it into a *variable*, and *array element*, or a *subroutine
     * call*. A single lookahead token, which may be `[`, `(`, or `.`, suffices
     * to distinguish between the possibilities. Any other token is not part of
     * this term and should not be advanced over:
     * 
     * integerConstant | stringConstant | keywordConstant | varName | 
     * varname'[' expression ']' | subroutineCall | '**(**' expression '**)**' | 
     * unaryOp term
     */
    compileTerm(): void;
    /**
     * Compiles a (possibly empty) comma-separated list of expressions:
     * 
     * (expression (',' expression)*)?
     * 
     * @returns The number of expressions in the list.
     */
    compileExpressionList(): number;
}