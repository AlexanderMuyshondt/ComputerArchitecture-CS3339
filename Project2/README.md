# CS3339 Project 2 rev3
## Description
In this project, you will extend your ARM disassembler with a simulator.
## Part 2: Simulator
Your program will create an instruction-by-instruction simulation of the ARM program. This simulation will execute instructions sequentially (non-pipelined) and output the contents of all registers and memory (the state of the processor and memory) after each instruction. You will not have to implement exception/interrupt handling.

Instructions: ( all arg refs to machine not assembly instruction - based on my code - your milage may vary) I will add more as I completely test them in my code.

B: Extends and shifts (multipies by 4) the 26 bit argument (words) in arg1 and adds the value to the PC.

CBZ, CBNZ: Does comparison against zero of arg2 and if condition met adds extended and shifted offset to the PC. Offset can be positive or negative. Offset in words.

ADDI: Adds extended immediate value to the value in arg1 register and puts value in arg3 register. Immediate can be positive or negative.

SUBI: Subtracts extended immediate value from the value in arg1 register and puts value in arg3 register. Immediate can be positive or negative

ALL R FORMAT: arg2 register <operation>arg1 register result into arg3 register.
  
MOVZ: 16 bit pattern in arg3 register shifted left by either 0,16,32,48 positions determined by 2 bit arg1 value and written into zeroed arg2 register

MOVK: 16 bit pattern in arg3 register shifted left by either 0,16,32,48 positions determined by 2 bit arg1 value and written into arg2 register leaving all other bits intact.

ASR: This is ">>" will divide by 2.

LSR: This is a pattern shift. Whatever is in register is shifted right with zero fill. LSL: Shift left arg2 positions adding zeros on the right.
