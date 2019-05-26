# CS3339 Computer Architecture - Project 1
## Simple LegV8 Disassembler
This project reads in a subset of instructions from the LegV8 machine language and disassembles it into the corresponding LegV8 assembly language instructions. The assembly instructions and any data are output to a `.txt` file, and information about the instructions and data read from the machine code are stored in data structures in the `Disassemble` class to be used in the next project, a simulator.

### Usage
To run, compile the program with python 2.7 and supply arguments from the command line detailing the input file path and output file. For example:

`python team13_project1.py -i test1_bin.txt -o team13_out_dis`

The input file path is read from the `-i` argument. This needs to be the full path of the input file (or just the name if the file is in the working directory).

The output filename is read from the `-o` argument. Whatever is entered here will have `.txt` appended to it and that file will be saved with the output in it in the working directory.
