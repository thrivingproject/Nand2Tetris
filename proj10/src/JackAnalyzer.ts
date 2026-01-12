import fs from 'node:fs';
import path from 'node:path';

import { TokenType, type Keyword } from "./enums.js";
import JackTokenizer from "./JackTokenizer.js";
import CompilationEngine from "./CompilationEngine.js";

/**
 * Process a single `.jack` file.
 * 
 * @param filepath path to `.jack` file
 */
function processJackFile(filepath: string) {
    const jt = new JackTokenizer(filepath);
    while (jt.hasMoreTokens()) {
        jt.advance();
        const tokenType = jt.tokenType();
        let token: Keyword | string;
        switch (tokenType) {
            case TokenType.IDENTIFIER:
                token = jt.identifier();
                break;
            case TokenType.INT_CONST:
                token = jt.intVal().toString();
                break;
            case TokenType.KEYWORD:
                token = jt.keyWord();
                break;
            case TokenType.SYMBOL:
                token = jt.symbol();
                break;
            case TokenType.STRING_CONST:
                token = jt.stringVal();
                break;
            default:
                throw new Error(`Unrecognized token type. ${tokenType}`);
        }
        console.log(tokenType, token);
    }
}


const arg = process.argv[2];
if (arg !== undefined) {
    const stats = fs.statSync(arg);
    if (stats.isFile())
        if (!arg.endsWith(".jack"))
            throw new Error("The source file must have a .jack extension.");
        else
            processJackFile(arg);
    else if (stats.isDirectory()) {
        const dir = fs.opendirSync(arg);
        let dirent;
        while ((dirent = dir.readSync()))
            if (dirent.isFile() && dirent.name.endsWith(".jack"))
                processJackFile(path.join(arg, dirent.name));
        dir.closeSync();
    }
    else
        throw new Error("The source must be a directory or a file.");
}
else
    throw Error("Usage: node dist/JackAnalyzer.js source");


