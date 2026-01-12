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
    const xmlFilePath = filepath.replace(".jack", "C.xml");
    const engine = new CompilationEngine(jt, xmlFilePath);
    engine.compileClass();
    return;
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
