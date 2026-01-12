import type { I_CompilationEngine } from "./interfaces.js";

export default class CompilationEngine implements I_CompilationEngine {
    /**
     * Creates a new compilation engine with the given input and output. The
     * next routine called (by the `JackAnalyzer`) must be `compileClass`.
     * 
     * @param input input file path
     * @param output output file path
     */
    constructor (input: string, output: string) { }

    compileClass(): void {
        throw new Error("Method not implemented.");
    }
    compileClassVarDec(): void {
        throw new Error("Method not implemented.");
    }
    compileSubroutine(): void {
        throw new Error("Method not implemented.");
    }
    compileParameterList(): void {
        throw new Error("Method not implemented.");
    }
    compileSubroutineBody(): void {
        throw new Error("Method not implemented.");
    }
    compileVarDec(): void {
        throw new Error("Method not implemented.");
    }
    compileStatements(): void {
        throw new Error("Method not implemented.");
    }
    compileLet(): void {
        throw new Error("Method not implemented.");
    }
    compileIf(): void {
        throw new Error("Method not implemented.");
    }
    compileWhile(): void {
        throw new Error("Method not implemented.");
    }
    compileDo(): void {
        throw new Error("Method not implemented.");
    }
    compileReturn(): void {
        throw new Error("Method not implemented.");
    }
    compileExpression(): void {
        throw new Error("Method not implemented.");
    }
    compileTerm(): void {
        throw new Error("Method not implemented.");
    }
    compileExpressionList(): number {
        throw new Error("Method not implemented.");
    }
}