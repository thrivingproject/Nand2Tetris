import fs from 'node:fs';
import type { I_CompilationEngine } from "./interfaces.js";
import type JackTokenizer from "./JackTokenizer.js";
import { Keyword, TokenType, statementKeywords, ops } from './enums.js';

/**
 * Gets its input from a JackTokenizer, and emits its output to an output file,
 * using parsing routines. Each parsing routine *compilexxx* is responsible for
 * handling all the tokens that make up the construct *xxx*, advancing the
 * tokenizer exactly beyond these tokens and outputting the parsing of *xxx*.
 */
export default class CompilationEngine implements I_CompilationEngine {
    private xmlBody = "";
    private _indentLvl: number;
    private readonly SPACES_PER_INDENT = 2;

    /**
     * Creates a new compilation engine with the given input and output. The
     * next routine called (by the `JackAnalyzer`) must be `compileClass`.
     * 
     * @param input tokenizer
     * @param output output file path
     */
    constructor (private input: JackTokenizer, private output: string) {
        this._indentLvl = 0;
    }

    /**
     * Get current indentation spaces.
     * @returns spaces
     */
    private getIndents(): string {
        return " ".repeat(this._indentLvl * this.SPACES_PER_INDENT);
    }
    private writeToken() {
        let token: Keyword | string;
        let tag: string;
        switch (this.input.tokenType()) {
            case TokenType.IDENTIFIER:
                tag = "identifier";
                token = this.input.identifier();
                break;
            case TokenType.INT_CONST:
                tag = "integerConstant";
                token = this.input.intVal().toString();
                break;
            case TokenType.KEYWORD:
                tag = "keyword";
                token = this.input.keyWord();
                break;
            case TokenType.STRING_CONST:
                token = this.input.stringVal().replace(/"/g, "");
                tag = "stringConstant";
                break;
            case TokenType.SYMBOL:
                tag = "symbol";
                token = this.input.symbol();
                if (token === "<")
                    token = "&lt;";
                else if (token === ">")
                    token = "&gt;";
                else if (token === "&")
                    token = "&amp;";
                else if (token === '"')
                    token = "&quot;";
                break;
        }
        this.xmlBody += `${this.getIndents()}<${tag}> ${token} </${tag}>\n`;
    }
    /**
     * Write the tag of the construct, add indent level
     * @param construct The name of construct, eg., classVarDec, parameterList
     */
    private writeConstructTagAndIndent(construct: string) {
        this.writeTag(`<${construct}>`);
        this._indentLvl += 1;
    }
    /**
     * Write the end tag of the construct, decrease indent level
     * @param constructName The name of construct, eg., letStatement, varDec
     */
    private writeConstructTagAndDedent(constructName: string) {
        this._indentLvl -= 1;
        this.writeTag(`</${constructName}>`);
    }
    private writeTag(tag: string) {
        this.xmlBody += `${this.getIndents()}${tag}\n`;
    }
    /**
     * Advance if there are more tokens, else throw error
     * @param expected expected token type
     */
    private advanceInput(): void {
        if (this.input.hasMoreTokens()) this.input.advance();
        else throw new Error("Unexpected end of tokens.");
    }
    /**
     * Throw error if current token type is not expected type
     * @param expected expected token type
     */
    private _expectTokenType(expected: TokenType): void {
        const currentType = this.input.tokenType();
        if (this.input.tokenType() !== expected) {
            throw new Error(`Expected ${expected}, got ${currentType}`);
        }
    }
    /**
     * Throw an error if the current token is not a symbol or symbol is not the
     * expected symbol. Can write token.
     * @param expected the symbol expected
     * @param options write option
     */
    private expectSymbol(
        expected?: string | string[],
        options?: { write: boolean; }
    ): void {
        const write = options?.write ?? false;
        this._expectTokenType(TokenType.SYMBOL);
        if (expected !== undefined) {
            const symbol = this.input.symbol();
            const isArr = Array.isArray(expected);
            if (
                (isArr && !expected.includes(symbol)) ||
                (!isArr && expected !== symbol)
            ) {
                throw new Error(
                    `Expected symbol '${expected}', got '${symbol}'`
                );
            }
        }
        if (write) this.writeToken();
    }
    /**
     * First check if current token is a Keyword and throw error if not. Then,
     * if expected is an array, check if the current token is one of the
     * keywords in the array; otherwise, check if the current token is the
     * provided Keyword.
     * @param expected expected keyword
     * @param options write option
     */
    private expectKeyword(
        expected?: Keyword | Keyword[],
        options?: { write: boolean; }
    ) {
        const write = options?.write ?? false;
        this._expectTokenType(TokenType.KEYWORD);
        if (expected !== undefined) {
            const kw = this.input.keyWord();
            const isArr = Array.isArray(expected);
            if (
                (isArr && !expected.includes(kw)) ||
                (!isArr && expected !== kw)
            ) {
                throw new Error(`Expected keyword '${expected}', got '${kw}'`);
            }
        }
        if (write) this.writeToken();
    }
    /**
     * Throw an error if the current token is not an identifier.
     */
    private expectIdentifier(options?: { write: boolean; }) {
        this._expectTokenType(TokenType.IDENTIFIER);
        const write = options?.write ?? false;
        if (write) this.writeToken();
    }


    compileClass(): void {
        this.writeConstructTagAndIndent("class");
        this.advanceInput();
        this.expectKeyword(Keyword.CLASS, { write: true });
        this.advanceInput();
        this.expectIdentifier({ write: true });
        this.advanceInput();
        this.expectSymbol('{', { write: true });
        this.advanceInput();
        while (this.input.tokenType() === TokenType.KEYWORD) {
            const kw = this.input.keyWord();
            switch (kw) {
                case Keyword.STATIC:
                case Keyword.FIELD:
                    this.compileClassVarDec();
                    break;
                case Keyword.CONSTRUCTOR:
                case Keyword.FUNCTION:
                case Keyword.METHOD:
                    this.compileSubroutineDec();
                    break;
                default:
                    throw new Error(`Unexpected keyword in class: ${kw}`);
            }
        }
        this.expectSymbol('}', { write: true });
        if (this.input.hasMoreTokens()) {
            throw new Error("Expected EOF.");
        }
        this.writeConstructTagAndDedent("class");
        fs.writeFileSync(this.output, this.xmlBody);
    }
    compileClassVarDec(): void {
        this.writeConstructTagAndIndent("classVarDec");
        this.expectKeyword([Keyword.STATIC, Keyword.FIELD], { write: true });
        this.advanceInput();
        this.writeToken();  // type
        this.advanceInput();
        this.expectIdentifier({ write: true });  // varName
        this.advanceInput();
        while (
            this.input.tokenType() === TokenType.SYMBOL
            && this.input.symbol() === ','
        ) {
            this.writeToken();
            this.advanceInput();
            this.expectIdentifier({ write: true });  // varName
            this.advanceInput();
        }
        this.expectSymbol(';', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("classVarDec");
    }
    compileSubroutineDec(): void {
        this.writeConstructTagAndIndent("subroutineDec");
        this.expectKeyword(
            [Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD],
            { write: true }
        );
        this.advanceInput();
        this.writeToken();  // ('void' | type)
        this.advanceInput();
        this.expectIdentifier({ write: true });  // subroutineName
        this.advanceInput();
        this.expectSymbol('(', { write: true });
        this.advanceInput();
        this.compileParameterList();
        this.expectSymbol(')', { write: true });
        this.advanceInput();
        this.compileSubroutineBody();
        this.writeConstructTagAndDedent("subroutineDec");
    }
    compileParameterList(): void {
        this.writeConstructTagAndIndent("parameterList");
        while (true) {
            if (
                this.input.tokenType() === TokenType.SYMBOL &&
                this.input.symbol() === ')'
            ) {
                break;
            }
            this.writeToken();
            this.advanceInput();
        }
        this.writeConstructTagAndDedent("parameterList");
    }
    compileSubroutineBody(): void {
        this.writeConstructTagAndIndent("subroutineBody");
        this.expectSymbol('{', { write: true });
        this.advanceInput();
        while (
            this.input.tokenType() === TokenType.KEYWORD &&
            this.input.keyWord() === Keyword.VAR
        ) {
            this.compileVarDec();
        }
        this.compileStatements();
        this.expectSymbol('}', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("subroutineBody");
    }
    compileVarDec(): void {
        this.writeConstructTagAndIndent("varDec");
        this.expectKeyword(Keyword.VAR, { write: true });
        this.advanceInput();
        this.writeToken();  // type
        this.advanceInput();
        this.writeToken();  // varName
        this.advanceInput();
        while (
            this.input.tokenType() === TokenType.SYMBOL &&
            this.input.symbol() === ','
        ) {
            this.writeToken();
            this.advanceInput();
            this.writeToken();  // varName
            this.advanceInput();
        }
        this.expectSymbol(';', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("varDec");
    }
    compileStatements(): void {
        this.writeConstructTagAndIndent("statements");
        while (
            this.input.tokenType() === TokenType.KEYWORD &&
            statementKeywords.includes(this.input.keyWord())
        ) {
            switch (this.input.keyWord()) {
                case Keyword.LET:
                    this.compileLet();
                    break;
                case Keyword.IF:
                    this.compileIf();
                    break;
                case Keyword.WHILE:
                    this.compileWhile();
                    break;
                case Keyword.RETURN:
                    this.compileReturn();
                    break;
                case Keyword.DO:
                    this.compileDo();
                    break;
            }
        }
        this.writeConstructTagAndDedent("statements");
    }
    compileLet(): void {
        this.writeConstructTagAndIndent("letStatement");
        this.expectKeyword(Keyword.LET, { write: true });
        this.advanceInput();
        this.expectIdentifier({ write: true });
        this.advanceInput();
        this.expectSymbol();
        if (this.input.symbol() === '[') {
            this.writeToken(); this.advanceInput();  // write the '['
            this.compileExpression();
            this.expectSymbol(']', { write: true });
            this.advanceInput();
        }
        this.expectSymbol('=', { write: true });
        this.advanceInput();
        this.compileExpression();
        this.expectSymbol(';', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("letStatement");
    }
    compileIf(): void {
        this.writeConstructTagAndIndent("ifStatement");
        this.expectKeyword(Keyword.IF, { write: true });
        this.advanceInput();
        this.expectSymbol('(', { write: true });
        this.advanceInput();
        this.compileExpression();
        this.expectSymbol(')', { write: true });
        this.advanceInput();
        this.expectSymbol('{', { write: true });
        this.advanceInput();
        this.compileStatements();
        this.expectSymbol('}', { write: true });
        this.advanceInput();
        if (
            this.input.tokenType() === TokenType.KEYWORD &&
            this.input.keyWord() === Keyword.ELSE
        ) {
            this.writeToken();
            this.advanceInput();
            this.expectSymbol('{', { write: true });
            this.advanceInput();
            this.compileStatements();
            this.expectSymbol('}', { write: true });
            this.advanceInput();
        }
        this.writeConstructTagAndDedent("ifStatement");
    }
    compileWhile(): void {
        this.writeConstructTagAndIndent("whileStatement");
        this.expectKeyword(Keyword.WHILE, { write: true });
        this.advanceInput();
        this.expectSymbol('(', { write: true });
        this.advanceInput();
        this.compileExpression();
        this.expectSymbol(')', { write: true });
        this.advanceInput();
        this.expectSymbol('{', { write: true });
        this.advanceInput();
        this.compileStatements();
        this.expectSymbol('}', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("whileStatement");
    }
    compileDo(): void {
        this.writeConstructTagAndIndent("doStatement");
        this.expectKeyword(Keyword.DO, { write: true });

        // Needed to write either the subroutine name or the qualifier
        this.advanceInput();
        this.expectIdentifier({ write: true });

        // Expecting '.' or '(' since calls may or may not have a qualifier
        this.advanceInput();
        this.expectSymbol(['.', '(']);

        // Needed to handle subroutine calls that include a qualifier
        if (this.input.symbol() === '.') {
            this.writeToken();
            this.advanceInput();
            // Need to write subroutine name
            this.expectIdentifier({ write: true });
            this.advanceInput();
        }

        // '(' Expected in both cases
        this.expectSymbol('(', { write: true });
        this.advanceInput();
        this.compileExpressionList();
        this.expectSymbol(')', { write: true });
        this.advanceInput();
        this.expectSymbol(';', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("doStatement");
    }
    compileReturn(): void {
        this.writeConstructTagAndIndent("returnStatement");
        this.expectKeyword(Keyword.RETURN, { write: true });
        this.advanceInput();
        if (
            this.input.tokenType() !== TokenType.SYMBOL &&
            this.input.symbol() !== ';'
        ) {
            this.compileExpression();
        }
        this.expectSymbol(';', { write: true });
        this.advanceInput();
        this.writeConstructTagAndDedent("returnStatement");
    }
    compileExpression(): void {
        this.writeConstructTagAndIndent("expression");
        this.compileTerm();
        // (op term)*
        while (
            this.input.tokenType() === TokenType.SYMBOL &&
            ops.includes(this.input.symbol())
        ) {
            this.writeToken();
            this.advanceInput();
            this.compileTerm();
        }
        this.writeConstructTagAndDedent("expression");
    }
    compileTerm(): void {
        this.writeConstructTagAndIndent("term");
        switch (this.input.tokenType()) {
            case TokenType.KEYWORD:
                this.expectKeyword(
                    [Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS],
                    { write: true }
                );
                this.advanceInput();
                break;
            case TokenType.INT_CONST:
            case TokenType.STRING_CONST:
            case TokenType.IDENTIFIER:  // subroutineCall, varName
                this.writeToken();
                this.advanceInput();
                // Need to handle subroutineCalls and varName[expression] terms
                if (this.input.tokenType() === TokenType.SYMBOL) {
                    const symbol = this.input.symbol();
                    if (symbol === '[') {                          // Array
                        this.writeToken();
                        this.advanceInput();
                        this.compileExpression();
                        this.expectSymbol(']', { write: true });
                        this.advanceInput();
                    } else if (['(', '.'].includes(symbol)) {      // Subroutine
                        if (this.input.symbol() === '.') {
                            this.writeToken();
                            this.advanceInput();
                            this.expectIdentifier({ write: true });
                            this.advanceInput();
                        }
                        this.expectSymbol('(', { write: true });
                        this.advanceInput();
                        this.compileExpressionList();
                        this.expectSymbol(')', { write: true });
                        this.advanceInput();
                    } // No else clause since any symbol could exist here
                }
                break;
            case TokenType.SYMBOL:
                // Need to handle `unaryOp term` and `'(' expression ')'`
                this.expectSymbol(['(', '~', '-'], { write: true });
                const symbol = this.input.symbol();
                this.advanceInput();
                if (symbol === '(') {
                    this.compileExpression();
                    this.expectSymbol(')', { write: true });
                    this.advanceInput();
                } else this.compileTerm();
                break;
            default:
                break;
        }
        this.writeConstructTagAndDedent("term");
    }
    compileExpressionList(): number {
        this.writeConstructTagAndIndent("expressionList");
        let count = 0;
        if (
            this.input.tokenType() !== TokenType.SYMBOL ||
            this.input.symbol() !== ')'
        ) {
            this.compileExpression();
            count++;
            while (
                this.input.tokenType() === TokenType.SYMBOL &&
                this.input.symbol() === ','
            ) {
                this.writeToken();
                this.advanceInput();
                this.compileExpression();
                count++;
            }
        }
        this.writeConstructTagAndDedent("expressionList");
        return count;
    }
}
