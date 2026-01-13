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

    /**
     * Write the tag of the construct, add indent level
     * @param construct The name of construct, eg., classVarDec, parameterList
     */
    private writeConstructTagAndIndent(construct: string) {
        this.writeTag(`<${construct}>`);
        this.indentLvl += 1;
    }

    /**
     * Write the end tag of the construct, decrease indent level
     * @param constructName The name of construct, eg., letStatement, varDec
     */
    private writeConstructTagAndDedent(constructName: string) {
        this.indentLvl -= 1;
        this.writeTag(`</${constructName}>`);
    }

    private writeTag(tag: string) {
        this.xmlBody += `${this.getIndents()}${tag}\n`;
    }

    compileClass(): void {
        this.writeConstructTagAndIndent("class");
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
                    this.compileSubroutineDec();
                    break;
                default:
                    // Needed to Write 'class', className and brackets
                    this.writeToken();
                    break;
            }
        }
        this.writeConstructTagAndDedent("class");
        fs.writeFileSync(this.output, this.xmlBody);
    }
    compileClassVarDec(): void {
        this.writeConstructTagAndIndent("classVarDec");
        // Needed to write 'static' or 'field' token advanced to in compileClass
        this.writeToken();
        while (this.input.hasMoreTokens()) {
            this.input.advance();
            this.writeToken();
            const isSymbol = this.input.tokenType() === TokenType.SYMBOL;
            if (isSymbol && this.input.symbol() === ';') break;
        }
        this.writeConstructTagAndDedent("classVarDec");
    }
    compileSubroutineDec(): void {
        this.writeConstructTagAndIndent("subroutineDec");
        // Needed to write token advanced to in compileClass
        this.writeToken();
        while (this.input.hasMoreTokens()) {
            this.input.advance();
            this.writeToken();
            if (this.input.tokenType() === TokenType.SYMBOL) {
                if (this.input.symbol() === '(') {
                    this.compileParameterList();
                    // Safe since we checked for token and advanced in paramList
                    this.writeToken();  // Should be `)`
                    this.compileSubroutineBody();
                    break;
                }
            }
        }
        this.writeConstructTagAndDedent("subroutineDec");
    }
    compileParameterList(): void {
        this.writeConstructTagAndIndent("parameterList");
        while (this.input.hasMoreTokens()) {
            this.input.advance();
            // Needed so `)` is written in `compileSubroutine` instead of here
            if (
                this.input.tokenType() === TokenType.SYMBOL &&
                this.input.symbol() === ')'
            ) {
                break;
            }
            this.writeToken();
        }
        this.writeConstructTagAndDedent("parameterList");
    }
    compileSubroutineBody(): void {
        this.writeConstructTagAndIndent("subroutineBody");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("subroutineBody");
    }
    compileVarDec(): void {
        this.writeConstructTagAndIndent("varDec");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("varDec");
    }
    compileStatements(): void {
        this.writeConstructTagAndIndent("statements");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("statements");
    }
    compileLet(): void {
        this.writeConstructTagAndIndent("letStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("letStatement");
    }
    compileIf(): void {
        this.writeConstructTagAndIndent("ifStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("ifStatement");
    }
    compileWhile(): void {
        this.writeConstructTagAndIndent("whileStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("whileStatement");
    }
    compileDo(): void {
        this.writeConstructTagAndIndent("doStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("doStatement");
    }
    compileReturn(): void {
        this.writeConstructTagAndIndent("returnStatement");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("returnStatement");
    }
    compileExpression(): void {
        this.writeConstructTagAndIndent("expression");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("expression");
    }
    compileTerm(): void {
        this.writeConstructTagAndIndent("term");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("term");
    }
    compileExpressionList(): number {
        this.writeConstructTagAndIndent("expression list");
        while (this.input.hasMoreTokens()) { break; }
        this.writeConstructTagAndDedent("expression list");
        // TODO: change 0
        return 0;
    }
}