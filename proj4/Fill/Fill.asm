// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.
// Screen organized as 256 rows of 512 pixels (32 16-bit words) per row. 

// Set pointer to current screen address
@SCREEN
D=A
@current
M=D
// Save last screen address (SCREEN + 32 * 256 - 1) @last
@8191
D=D+A
@last
M=D

(CHECK)
   // Get current screen address
   @current
   D=M
   // check input
   @KBD
   D=M
   // Jump to whiten if no input
   @WHITEN
   D;JEQ
   // Blacken current address
   @current
   D=M
   A=D
   M=-1
   // if current screen address >= last screen address, jump to check
   @current
   D=M
   @last
   D=D-M
   @CHECK
   D;JGE
   // increment current screen address
   @current
   M=M+1
   // jump to CHECK
   @CHECK
   0;JMP

   (WHITEN)
   // whiten current address
   @current
   D=M
   A=D
   M=0
   // if current screen address <= SCREEN, jump to CHECK
   @current
   D=M
   @SCREEN
   D=D-A
   @CHECK
   D;JLE
   // decrement current screen address
   @current
   M=M-1
   // jump to CHECK
   @CHECK
   0;JMP
