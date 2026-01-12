import fs from 'node:fs';
import type { I_CompilationEngine } from "./interfaces.js";
import type JackTokenizer from "./JackTokenizer.js";
import { Keyword, TokenType } from './enums.js';

/**
 * Gets its input from a JackTokenizer, and emits its output to an output file,
 * using parsing routines. Each parsing routine *compilexxx* is responsible for
 * handling all the tokens that make up the construct *xxx*, advancing the
 * tokenizer exactly beyond these tokens and outputting the parsing of *xxx*.
 */
export default class CompilationEngine implements I_CompilationEngine {
    private xmlBody = "";
    private indentLvl: number;
    private readonly SPACES_PER_INDENT = 2;

    /**
     * Creates a new compilation engine with the given input and output. The
     * next routine called (by the `JackAnalyzer`) must be `compileClass`.
     * 
     * @param input tokenizer
     * @param output output file path
     */
    constructor (private input: JackTokenizer, private output: string) {
        this.indentLvl = 0;
        if (!this.input.hasMoreTokens())
            throw new Error("Class not found.");
        this.input.advance();
    }

    /**
     * Get current indentation spaces.
     * @returns spaces
     */
    private getIndents(): string {
        return " ".repeat(this.indentLvl * this.SPACES_PER_INDENT);
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

    private startNonTerminalConstruct(construct: string) {
        this.writeTag(`<${construct}>`);
        this.indentLvl += 1;
        this.writeToken();
    }

    private endNonTerminalConstruct(tagName: string) {
        this.indentLvl -= 1;
        this.writeTag(`</${tagName}>`);
    }

    private writeTag(tag: string) {
        this.xmlBody += `${this.getIndents()}${tag}\n`;
    }

    compileClass(): void {
        this.startNonTerminalConstruct("class");
        while (this.input.hasMoreTokens()) {
            this.input.advance();
            // Needed to write variable and subroutine declarations
            const keyword = this.input.tokenType() === TokenType.KEYWORD
                && this.input.keyWord();
            switch (keyword) {
                case Keyword.STATIC:
                case Keyword.FIELD:
                    this.compileClassVarDec();
                    break;
                case Keyword.CONSTRUCTOR:
                case Keyword.FUNCTION:
                case Keyword.METHOD:
                    this.compileSubroutine();
                    break;
                default:
                    // Needed to Write 'class', className and brackets
                    this.writeToken();
                    break;
            }
        }
        this.endNonTerminalConstruct("class");
        fs.writeFileSync(this.output, this.xmlBody);
    }
    compileClassVarDec(): void {
        this.startNonTerminalConstruct("classVarDec");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("classVarDec");
    }
    compileSubroutine(): void {
        this.startNonTerminalConstruct("subroutineDec");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("subroutineDec");
    }
    compileParameterList(): void {
        this.startNonTerminalConstruct("parameterList");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("parameterList");
    }
    compileSubroutineBody(): void {
        this.startNonTerminalConstruct("subroutineBody");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("subroutineBody");
    }
    compileVarDec(): void {
        this.startNonTerminalConstruct("varDec");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("varDec");
    }
    compileStatements(): void {
        this.startNonTerminalConstruct("statements");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("statements");
    }
    compileLet(): void {
        this.startNonTerminalConstruct("letStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("letStatement");
    }
    compileIf(): void {
        this.startNonTerminalConstruct("ifStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("ifStatement");
    }
    compileWhile(): void {
        this.startNonTerminalConstruct("whileStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("whileStatement");
    }
    compileDo(): void {
        this.startNonTerminalConstruct("doStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("doStatement");
    }
    compileReturn(): void {
        this.startNonTerminalConstruct("returnStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("returnStatement");
    }
    compileExpression(): void {
        this.startNonTerminalConstruct("expression");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("expression");
    }
    compileTerm(): void {
        this.startNonTerminalConstruct("term");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("term");
    }
    compileExpressionList(): number {
        this.startNonTerminalConstruct("expression list");
        while (this.input.hasMoreTokens()) { break; }
        this.endNonTerminalConstruct("expression list");
        // TODO: change 0
        return 0;
    }
}