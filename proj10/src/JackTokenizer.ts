import { keywords, symbols, TokenType, type Keyword } from "./enums.js";
import type { I_JackTokenizer } from "./interfaces.js";
import { readFileSync } from 'node:fs';


/**
 * This class ignores all comments and white space in the input stream and
 * enables accessing the input one token at a time. Also, it parses and provides
 * the *type* of each token, as defined by the Jack grammar.
 */
export default class JackTokenizer implements I_JackTokenizer {
    private tokenStream: string;
    private currentToken: string;

    /**
     * Open the input `.jack` file and get ready to tokenize it.
     * @param input The input stream
     */
    constructor (input: string) {
        const text = readFileSync(input, 'utf8');
        this.tokenStream = this.removeComments(text);
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
            // Trim left so we can test if line starts with "/*"
            const line = result.value.trimStart();
            if (line.startsWith("/*")) {
                while (!result.done && !result.value.includes("*/"))
                    result = lineIter.next();
            } else {
                // Split to put code without comment in arr[0]
                const [code, ..._] = line.split("//");
                // Check for truthiness to ignore empty lines
                if (code)
                    // Trim end since splitting at inline comment leaves space
                    cleanedText += code.trimEnd();
            }
            // Advance iterator to assess line after comment / cleaned code line 
            result = lineIter.next();
        }
        return cleanedText;
    }
    hasMoreTokens(): boolean {
        return Boolean(this.tokenStream);
    }
    advance(): void {
        // reset current token
        this.currentToken = "";
        /** Use to track how many chars we consume from tokenStream */
        let charsConsumed = 0;

        // Different logic for string constant and other tokens
        if (this.tokenStream[0] === '"') {
            const indexOfClosingQuote = this.tokenStream.indexOf('"', 1);
            charsConsumed = indexOfClosingQuote + 1;
            this.currentToken = this.tokenStream.slice(0, charsConsumed);
        } else {
            for (const char of this.tokenStream) {
                if (symbols.includes(char)) {
                    // Only consume if symbol is token so we can consume later
                    if (charsConsumed === 0) {
                        this.currentToken = char;
                        charsConsumed++;
                    }
                    break;
                } else if (char === ' ') {
                    // Don't consume space since we'll trim before returning
                    break;
                } else {
                    // Build up token
                    this.currentToken += char;
                    charsConsumed++;
                }
            }
        }
        // Need so next call starts with first char of next token
        const unconsumed = this.tokenStream.slice(charsConsumed);
        this.tokenStream = unconsumed.trimStart();
    }
    tokenType(): TokenType {
        if (symbols.includes(this.currentToken))
            return TokenType.SYMBOL;
        else if (keywords.has(this.currentToken))
            return TokenType.KEYWORD;
        else if (Number.isInteger(Number.parseInt(this.currentToken)))
            return TokenType.INT_CONST;
        else if (this.currentToken[0] === '"')
            return TokenType.STRING_CONST;
        else return TokenType.IDENTIFIER;
    }
    keyWord(): Keyword {
        const keyword = keywords.get(this.currentToken);
        if (keyword === undefined)
            throw new Error(
                `Current token is not a keyword: ${this.currentToken}.`
            );
        return keyword;
    }
    symbol(): string {
        return this.currentToken;
    }
    identifier(): string {
        return this.currentToken;
    }
    intVal(): number {
        return Number.parseInt(this.currentToken);
    }
    stringVal(): string {
        return this.currentToken;
    }
}
