import { TokenType, type Keyword } from "./enums.js";
import JackTokenizer from "./JackTokenizer.js";

const jt = new JackTokenizer('test/Square/SquareGame.jack');

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