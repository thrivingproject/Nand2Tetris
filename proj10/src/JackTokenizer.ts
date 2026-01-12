import { keywords, symbols, TokenType, type Keyword } from "./enums.js";
import type { I_JackTokenizer } from "./interfaces.js";
import { readFileSync } from 'node:fs';


/**
 * This class ignores all comments and white space in the input stream and
 * enables accessing the input one token at a time. Also, it parses and provides
 * the *type* of each token, as defined by the Jack grammar.
 */
export default class JackTokenizer implements I_JackTokenizer {
    private readonly tokenStream: string;
    private index: number;
    private currentToken: string;

    /**
     * Open the input `.jack` file and get ready to tokenize it.
     * @param input The input stream
     */
    constructor (input: string) {
        const text = readFileSync(input, 'utf8');
        this.tokenStream = this.removeComments(text);
        this.index = 0;
        this.currentToken = "";
    }

    /**
     * Remove comments. Inline comments start with `//`, block with `/*`
     * 
     * @param text The input text
     */
    private removeComments(text: string): string {
        let cleanedText = "";
        const lines = text.split('\n');
        const lineIter = lines[Symbol.iterator]();
        let result = lineIter.next();
        while (!result.done) {
            // Trim so we can use startsWith
            const trimmed = result.value.trim();
            if (trimmed.startsWith("/*")) {
                // Skip lines until */ since that's where comment ends
                while (!result.done && !result.value.includes("*/"))
                    result = lineIter.next();
            } else {
                const [code, ..._] = trimmed.split("//");
                if (code)
                    cleanedText += code;
            }
            // Advance iterator to assess line after comment / cleaned code line 
            result = lineIter.next();
        }
        return cleanedText;
    }
    hasMoreTokens(): boolean {
        return this.index < this.tokenStream.length;
    }
    advance(): void {
        throw new Error("Method not implemented.");
    }
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

// (function () {
//     const jt = new JackTokenizer('test/Square/SquareGame.jack');
//     console.log(jt.tokenStream);
// })();

