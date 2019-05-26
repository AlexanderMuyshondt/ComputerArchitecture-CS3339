import sys


class Disassembler:
    # bit groupings for printing a spaced out instruction
    inst_spacing = [0, 8, 11, 16, 21, 26, 32]
    break_inst = 0xFEDEFFE7
    nop_inst = 0x00000000

    opcode_dict = {
        (0, 0): ['NOP', 'NOP'],
        (160, 191): ['B', 'B'],
        (1104, 1104): ['R', 'AND'],
        (1112, 1112): ['R', 'ADD'],
        (1160, 1161): ['I', 'ADDI'],
        (1360, 1360): ['R', 'ORR'],
        (1440, 1447): ['CB', 'CBZ'],
        (1448, 1455): ['CB', 'CBNZ'],
        # (1616, 1616): ['R', 'EOR'], # EOR opcode from book, wrong?
        (1872, 1872): ['R', 'EOR'],
        (1624, 1624): ['R', 'SUB'],
        (1672, 1673): ['I', 'SUBI'],
        (1684, 1687): ['IM', 'MOVZ'],
        (1692, 1692): ['R', 'ASR'],
        (1940, 1943): ['IM', 'MOVK'],
        (1690, 1690): ['R', 'LSR'],
        (1691, 1691): ['R', 'LSL'],
        (1984, 1984): ['D', 'STUR'],
        (1986, 1986): ['D', 'LDUR'],
        (2038, 2038): ['BREAK', 'BREAK']
    }

    def __init__(self):
        pass
    
    @staticmethod
    def tc_to_dec(bin_str):
        """
        Converts a two's complement binary string into a decimal integer
        :param bin_str: A two's complement binary string
        :return: The corresponding decimal integer
        """
        dec = int(bin_str, 2)
        # If positive, just convert to decimal
        if bin_str[0] == '0':
            return dec
        # If negative, flip bits and add 1, then multiply decimal by -1
        else:
            mask_str = '1' * len(bin_str)
            return -1 * ((dec ^ int(mask_str, 2)) + 1)

    @staticmethod
    def get_bits_as_decimal(high, low, b, signed=False):
        """
        Extracts a range of bits from a binary string as a decimal integer
        :param high: The leftmost desired bit
        :param low: The rightmost desired bit
        :param b: The binary string
        :return: The decimal value corresponding to the bots extracted from the binary string
        """
        mask_str = '0' * (31 - high) + '1' * (high - low + 1) + '0' * low
        mask_int = int(mask_str, 2)
        t1 = b & mask_int
        out = t1 >> low
        out_str = bin(out)[2:].zfill(high - low + 1)
        # if negative number and signed
        if out_str[0] == '1' and signed:
            return Disassembler.tc_to_dec(out_str)
        else:
            return out

    @staticmethod
    def get_bin_spaced(inst_dec):
        """
        Spaces a 32-bit string into groups of 8, 3, 5, 5, 5, 6
        :param inst_dec: The 32-bit binary string
        :return: The same string but spaced into the desired groups
        """
        inst_bin = '{0:032b}'.format(inst_dec)
        inst_spaced = ''
        for start, stop in zip(Disassembler.inst_spacing, Disassembler.inst_spacing[1:]):
            inst_spaced += inst_bin[start:stop] + ' '
        return inst_spaced

    @staticmethod
    def process(inst_dec):
        valid = False
        opcode = Disassembler.get_bits_as_decimal(31, 21, inst_dec)
        for (low, high), inst_info in Disassembler.opcode_dict.items():
            # Once correct range found, call appropriate function
            if low <= opcode <= high:
                f = getattr(Disassembler, '_Disassembler__process_' + inst_info[0].lower())
                return f(inst_dec, inst_info[1])

        if not valid:
            raise ValueError('ERROR: Invalid instruction: \'{0:032b}\''.format(inst_dec))

    @staticmethod
    def __process_r(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 21, inst_dec)
        rm = Disassembler.get_bits_as_decimal(20, 16, inst_dec)
        shamt = Disassembler.get_bits_as_decimal(15, 10, inst_dec)
        rn = Disassembler.get_bits_as_decimal(9, 5, inst_dec)
        rd = Disassembler.get_bits_as_decimal(4, 0, inst_dec)

        if inst_name == 'LSL' or inst_name == 'LSR' or inst_name == 'ASR':
            assembly = '{}\tR{}, R{}, #{}'.format(inst_name, rd, rn, shamt)
        else:
            assembly = '{}\tR{}, R{}, R{}'.format(inst_name, rd, rn, rm)

        return {
            'name': inst_name,
            'type': 'R',
            'opcode': opcode,
            'rm': rm,
            'shamt': shamt,
            'rn': rn,
            'rd': rd,
            'assembly': assembly
        }
    
    @staticmethod
    def __process_d(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 21, inst_dec)
        offset = Disassembler.get_bits_as_decimal(20, 12, inst_dec)
        op2 = Disassembler.get_bits_as_decimal(11, 10, inst_dec)
        rn = Disassembler.get_bits_as_decimal(9, 5, inst_dec)
        rt = Disassembler.get_bits_as_decimal(4, 0, inst_dec)

        assembly = '{}\tR{}, [R{}, #{}]'.format(inst_name, rt, rn, offset)

        return {
            'name': inst_name,
            'type': 'D',
            'opcode': opcode,
            'offset': offset,
            'op2': op2,
            'rn': rn,
            'rt': rt,
            'assembly': assembly
        }

    @staticmethod
    def __process_i(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 22, inst_dec)
        immediate = Disassembler.tc_to_dec('{0:012b}'.format(Disassembler.get_bits_as_decimal(21, 10, inst_dec)))
        rn = Disassembler.get_bits_as_decimal(9, 5, inst_dec)
        rd = Disassembler.get_bits_as_decimal(4, 0, inst_dec)

        assembly = '{}\tR{}, R{}, #{}'.format(inst_name, rd, rn, immediate)

        return {
            'name': inst_name,
            'type': 'I',
            'opcode': opcode,
            # TODO fix ALU so it can take immediate arguments
            'immediate': immediate,
            'rn': rn,
            'rd': rd,
            'assembly': assembly
        }

    @staticmethod
    def __process_b(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 24, inst_dec)
        address = Disassembler.get_bits_as_decimal(23, 0, inst_dec, signed=True)

        assembly = '{}\t#{}'.format(inst_name, address)

        return {
            'name': inst_name,
            'type': 'B',
            'opcode': opcode,
            'offset': address,
            'assembly': assembly
        }

    @staticmethod
    def __process_cb(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 24, inst_dec)
        offset = Disassembler.get_bits_as_decimal(23, 5, inst_dec, signed=True)
        rt = Disassembler.get_bits_as_decimal(4, 0, inst_dec)

        assembly = '{}\tR{}, #{}'.format(inst_name, rt, offset)

        return {
            'name': inst_name,
            'type': 'CB',
            'opcode': opcode,
            'offset': offset,
            'rt': rt,
            'assembly': assembly
        }

    @staticmethod
    def __process_im(inst_dec, inst_name):
        # Extract fields from machine instruction
        opcode = Disassembler.get_bits_as_decimal(31, 23, inst_dec)
        shamt = Disassembler.get_bits_as_decimal(22, 21, inst_dec)
        immediate = Disassembler.get_bits_as_decimal(20, 5, inst_dec)
        rd = Disassembler.get_bits_as_decimal(4, 0, inst_dec)

        assembly = '{}\tR{}, {}, LSL {}'.format(inst_name, rd, immediate, shamt * 16)

        return {
            'name': inst_name,
            'type': 'IM',
            'opcode': opcode,
            'shamt': shamt,
            'immediate': immediate,
            'rd': rd,
            'assembly': assembly
        }

    @staticmethod
    def __process_nop(inst_dec, inst_name):
        # TODO How should we change this for Project 3?
        # If the instruction isn't all 0s, raise error because opcode is zero -> invalid instruction
        if inst_dec != 0:
            bin_str = '{0:032b}'.format(inst_dec)
            raise ValueError('Invalid instruction on line {}: \'{}\''.format((self.__address - 96) / 4, bin_str))

        return {
            'name': inst_name,
            'type': 'NOP',
            'assembly': 'NOP'
        }

    @staticmethod
    def __process_break(inst_dec, inst_name):
        # TODO How should we change this for Project 3?
        
        return {
            'name': inst_name,
            'type': 'BREAK',
            'assembly': 'BREAK'
        }
