# CS3339 Project 3
## Description
In this project, you will create a simulator for a pipelined processor with cache.  Your simulator will support the instruction set described in Project 1, and must be able to load a binary ARM file and execute it.  Furthermore, your simulator will produce the disassembled program code (exactly as you did in Project 1), and will produce a cycle-by-cycle simulation showing the processor state at each cycle.  The processor state includes the contents of registers, buffers, cache, and data memory at each cycle. You do not need to implement exception/interrupt handling.

Implementation: You must implement this program in Python 2.7

It is highly recommended that in each cycle, your program execute each pipeline stage in REVERSE order.  That is, first handle the WB stage, then the MEM/ALU stages, then the ISSUE stage, then the IF stage.  By executing the pipelines in this order, you will ensure that the cache is updated in the proper order, and you will not have collisions in the buffers between pipeline stages.  This might give you some hint as how to structure your code.

## Execution:
Your program must accept command line arguments for execution.  The following arguments must be supported:  

	$ python team#_project2.py -i test1_bin.txt -o team#_out

	NOTE: I must be able to change the output file names using the -o argument

	assuming test1_bin.txt is the input file at that moment
	

Your program will produce 2 output files.  One named team#_out_pipeline.txt, which contains the simulation output, and one named team#_out_dis.txt, which contains the disassembled program code for the input ARM machine code.

Your program will be graded both with the sample input and output provided to you, and with input and output that is not provided to you.  It is recommended you construct your own input programs for testing.

## Expected Output:
Some sample inputs and expected outputs will be provided for testing.  I am going to give you the dis output.  You can extract the machine code input files that generated the dis file.  The most simple program is t1_dis.txt and they are progressively more complex in the following order: t1, t2, t3.  You will also get the sim output for each.
