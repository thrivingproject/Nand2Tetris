import { keywords, symbols, TokenType, type Keyword } from "./enums.js";
import type { I_JackTokenizer } from "./interfaces.js";
import { readFileSync } from 'node:fs';


/**
 * This class ignores all comments and white space in the input stream and
 * enables accessing the input one token at a time. Also, it parses and provides
 * the *type* of each token, as defined by the Jack grammar.
 */
export default class JackTokenizer implements I_JackTokenizer {
    private inInline = false;
    private inMultiline = false;
    private inStringConstant = false;

    /**
     * Open the input `.jack` file and get ready to tokenize it.
     * @param stream The input stream
     */
    constructor (stream: string) {
        const text = readFileSync(stream, 'utf8');
    }

    hasMoreTokens(): boolean {
        throw new Error("Method not implemented.");
    }
    advance(): void { }
    tokenType(): TokenType {
        throw new Error("Method not implemented.");
    }
    keyWord(): Keyword {
        throw new Error("Method not implemented.");
    }
    symbol(): string {
        throw new Error("Method not implemented.");
    }
    identifier(): string {
        throw new Error("Method not implemented.");
    }
    intVal(): number {
        throw new Error("Method not implemented.");
    }
    stringVal(): string {
        throw new Error("Method not implemented.");
    }
}
