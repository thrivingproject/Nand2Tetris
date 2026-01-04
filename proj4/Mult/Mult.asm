// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

    // init sum to 0
    @sum
    M=0
// check if R1 is zero
(LOOP)
    @R1
    D=M
    @LOOPEND
    D;JEQ
    // If not, add R0 to sum
    @R0
    D=M
    @sum
    M=D+M
    // Subract 1 from R1
    @R1
    M=M-1
    // Go back to check if R1 is zero
    @LOOP
    0;JMP
(LOOPEND)
    // Else save sum to R2
    @sum
    D=M
    @R2
    M=D
    // End
(END)
    @END
    0;JMP