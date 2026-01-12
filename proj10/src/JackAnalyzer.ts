import fs from 'node:fs';
import path from 'node:path';

import { TokenType, type Keyword } from "./enums.js";
import JackTokenizer from "./JackTokenizer.js";
import CompilationEngine from "./CompilationEngine.js";

/**
 * Process a single `.jack` file.
 * 
 * @param filepath path of `.jack` file
 */
function processJackFile(filepath: string) {
    const jt = new JackTokenizer(filepath);
    const xmlFilePath = filepath.replace(".jack", "T.xml");
    let xmlBody = getXmlBody(jt);
    fs.writeFileSync(xmlFilePath, `<tokens>\n${xmlBody}</tokens>`);
}

function getXmlBody(jt: JackTokenizer) {
    let xmlBody = "";
    while (jt.hasMoreTokens()) {
        jt.advance();
        let token: Keyword | string;
        let tag: string;
        switch (jt.tokenType()) {
            case TokenType.IDENTIFIER:
                tag = "identifier";
                token = jt.identifier();
                break;
            case TokenType.INT_CONST:
                tag = "integerConstant";
                token = jt.intVal().toString();
                break;
            case TokenType.KEYWORD:
                tag = "keyword";
                token = jt.keyWord();
                break;
            case TokenType.STRING_CONST:
                token = jt.stringVal().replace('"', "");
                tag = "stringConstant";
                break;
            case TokenType.SYMBOL:
                tag = "symbol";
                token = jt.symbol();
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
        xmlBody += `<${tag}> ${token} </${tag}>\n`;
    }
    return xmlBody;
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
