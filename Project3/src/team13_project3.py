import sys
from Disassembler import Disassembler
from WriteBackUnit import WriteBackUnit
from ALU import ALU
from MemoryUnit import MemoryUnit
from collections import deque
from RegisterFile import RegisterFile
from Cache import Cache
from IFUnit import IFUnit
from IssueUnit import IssueUnit


class SimplifiedSuperScalarSimulator:

    def __init__(self, infile, outfile, num_registers=32):
        self.__disassembler = Disassembler()

        self.__input_file = infile
        self.__output_file = outfile
        self.__f = open('team13_out_pipeline.txt', 'w')

        self.__pc = 96
        self.__cycle = 0

        self.__memory = {}
        self.__last_inst = 0

        self.pre_issue_size = 4
        self.pre_alu_size = 2
        self.pre_mem_size = 2
        self.post_alu_size = 1
        self.post_mem_size = 1

        self.__pre_issue_buffer = deque(maxlen=self.pre_issue_size)

        self.__pre_mem_buffer = deque(maxlen=self.pre_mem_size)
        self.__pre_alu_buffer = deque(maxlen=self.pre_alu_size)

        self.__post_mem_buffer = deque(maxlen=self.post_mem_size)
        self.__post_alu_buffer = deque(maxlen=self.post_alu_size)

        self.__cache_to_load = deque(maxlen=2)

        self.__register_file = RegisterFile(num_registers)
        self.__wb = WriteBackUnit(self.__register_file)
        self.__cache = Cache(self.__memory)
        self.__alu = ALU()
        self.__mem = MemoryUnit(self.__cache)
        self.__if = IFUnit(self.__cache, self.__register_file)
        self.__iu = IssueUnit(self.__register_file, self.__pre_issue_buffer,
                              self.__pre_mem_buffer, self.__pre_alu_buffer,
                              self.__post_mem_buffer, self.__post_alu_buffer
                              )

        self.__read_file()

    def __read_file(self):
        """
        Reads the designated input file and stores each line as a decimal integer
        """
        pc = 96
        with open(self.__input_file, 'r') as f:
            for line in f:
                self.__memory[pc] = int(line, 2)
                if int(line, 2) == Disassembler.break_inst:
                    self.__last_inst = pc
                pc += 4

    def __update_space(self):
        self.__pre_issue_space = self.pre_issue_size - len(self.__pre_issue_buffer)
        self.__pre_alu_space = self.pre_alu_size - len(self.__pre_alu_buffer)
        self.__pre_mem_space = self.pre_mem_size - len(self.__pre_mem_buffer)
        self.__post_alu_space = self.post_alu_size - len(self.__post_alu_buffer)
        self.__post_mem_space = self.post_mem_size - len(self.__post_mem_buffer)

    def __are_buffers_empty(self):
        self.__update_space()
        # print self.__pre_issue_space, \
        #     self.__pre_alu_space, \
        #     self.__pre_mem_space, \
        #     self.__post_alu_space, \
        #     self.__post_mem_space
        return self.__pre_issue_space == 4 and \
               self.__pre_alu_space == 2 and \
               self.__pre_mem_space == 2 and \
               self.__post_alu_space == 1 and \
               self.__post_mem_space == 1

    def run(self):
        run = True

        while run:
            run = False

            self.__cycle += 1
            print self.__cycle

            # Run WriteBackUnit
            if len(self.__post_mem_buffer) > 0:
                wb_in = self.__post_mem_buffer.popleft()
                self.__wb.run(wb_in, 'mem')
            if len(self.__post_alu_buffer) > 0:
                wb_in = self.__post_alu_buffer.popleft()
                self.__wb.run(wb_in, 'alu')

            self.__update_space()

            # Run ALU
            # If pre-buffer not empty and post-buffer not full
            if len(self.__pre_alu_buffer) > 0 and self.__post_alu_space > 0:
                alu_in = self.__pre_alu_buffer.popleft()
                alu_out = self.__alu.run(alu_in)
                self.__post_alu_buffer.append(alu_out)
                run = True

            self.__update_space()

            # Run MemoryUnit
            # If pre-buffer not empty and post-buffer not full
            if len(self.__pre_mem_buffer) > 0 and self.__post_mem_space > 0:
                mem_in = self.__pre_mem_buffer.popleft()
                mem_out = self.__mem.run(mem_in)
                if not mem_out:
                    self.__cache_to_load.append(mem_in['rn_val'] + mem_in['offset'])
                elif mem_out is not None:
                    self.__post_mem_buffer.append(mem_out)
                run = True

            self.__update_space()

            # Run Issue Unit (twice)
            # TODO Hazard detection
            if len(self.__pre_issue_buffer) > 0:
                self.__iu.run(self.__pre_mem_space, self.__pre_alu_space)
                run = True
                self.__update_space()

            # Run IF Unit
            # If pre-issue buffer not full
            result = True
            if self.__pc < self.__last_inst:
                if self.__pre_issue_space == 0:
                    continue
                elif self.__pre_issue_space == 1:
                    result = self.__if.run(self.__pc, 1)
                else:
                    result = self.__if.run(self.__pc, 2)
                if not result:
                    self.__cache_to_load.append(self.__pc)
                else:
                    insts = result[0]
                    self.__pc = result[1]
                    for inst in insts:
                        self.__pre_issue_buffer.append(inst)
                run = True

            self.__update_space()
            self.__print_state()

            while len(self.__cache_to_load) > 0:
                address = self.__cache_to_load.popleft()
                self.__cache.load(address)

    def __print_buffer(self, buffer):
        for i in range(buffer.maxlen):
            try:
                item = '[' + buffer[i]['assembly'] + ']'
            except IndexError:
                item = ''
            if item == '':
                self.__f.write('\tEntry {}:\n'.format(i, item))
            else:
                self.__f.write('\tEntry {}:\t{}\n'.format(i, item))

    def __print_buffers(self):
        self.__f.write('Pre-Issue Buffer:\n')
        self.__print_buffer(self.__pre_issue_buffer)

        self.__f.write('Pre_ALU Queue:\n')
        self.__print_buffer(self.__pre_alu_buffer)

        self.__f.write('Post_ALU Queue:\n')
        self.__print_buffer(self.__post_alu_buffer)

        self.__f.write('Pre_MEM Queue:\n')
        self.__print_buffer(self.__pre_mem_buffer)

        self.__f.write('Post_MEM Queue:\n')
        self.__print_buffer(self.__post_mem_buffer)

        self.__f.write('\n')

    def __print_registers(self):
        self.__f.write('Registers\n')
        for i in range(4):
            self.__f.write('R{:02d}:'.format(i * 8))
            for j in range(8):
                value = self.__register_file.read_register(i * 8 + j)
                self.__f.write('\t{}'.format(value))
            self.__f.write('\n')
        self.__f.write('\n')

    def __print_cache(self):
        self.__f.write('Cache\n')
        for s, set in enumerate(self.__cache.get_cache()):
            self.__f.write('Set {}: LRU={}\n'.format(s, set['lru']))
            for b, block in enumerate(set['blocks']):
                valid = int(block['valid'])
                dirty = int(block['dirty'])
                tag = int(block['tag']) if block['tag'] is not None else '0'
                content1 = '{0:032b}'.format(block['content'][0]) if (block['content'][0] != 0 and block['content'][0] is not None) else '0'
                content2 = '{0:032b}'.format(block['content'][1]) if (block['content'][1] != 0 and block['content'][1] is not None) else '0'

                self.__f.write('\tEntry {}:[({},{},{})<{},{}>]\n'.format(b, valid, dirty, tag, content1, content2))

        self.__f.write('\n')

    def __print_memory(self):
        self.__f.write('Data\n')

        # Filter data out of memory
        data = dict(self.__memory)
        for a in range(96, self.__last_inst + 4, 4):
            del data[a]

        # Fix stupid formatting, thanks Greg
        if len(data) > 0:
            # Add 0s from beginning to first
            first_data = min(data.keys())
            for a in range(self.__last_inst + 4, first_data, 4):
                data[a] = 0

            # Add 0s from last to end of line
            last_data = max(data.keys())
            a = last_data + 4
            while (a - first_data) % 8 != 0:
                data[a] = 0
                a += 4

        # Print useful information
        addresses = list(data.keys())
        addresses.sort()
        for i, addr in enumerate(addresses):
            if i % 8 == 0:
                self.__f.write('\n{}:\t{}'.format(addr, data[addr]))
            else:
                self.__f.write('\t{}'.format(data[addr]))
        self.__f.write('\n' * 2)

    def __print_state(self):
        self.__f.write('-' * 20 + '\n')
        self.__f.write('Cycle:{}\n\n'.format(self.__cycle))
        self.__print_buffers()
        self.__print_registers()
        self.__print_cache()
        self.__print_memory()


if __name__ == "__main__":
    infile = ''
    outfile = ''

    # Get in/out file from command line arguments
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            infile = sys.argv[i + 1]
        elif sys.argv[i] == '-o':
            outfile = sys.argv[i + 1]

    ssss = SimplifiedSuperScalarSimulator(infile, outfile)
    ssss.run()
