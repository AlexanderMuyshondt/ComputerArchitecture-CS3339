class ALU:

    def __init__(self):
        pass

    def run(self, alu_in):
        op = alu_in['op'].lower()

        # im instruction
        if alu_in['rn_val'] is None:
            arg1 = alu_in['imm_val']
            arg2 = alu_in['shamt_val']
        # i instruction
        elif 'imm_val' in alu_in.keys():
            arg1 = alu_in['rn_val']
            arg2 = alu_in['imm_val']
        # r instruction
        # shift
        elif op == 'lsl' or op == 'lsr' or op == 'asr':
            arg1 = alu_in['rn_val']
            arg2 = alu_in['shamt']
        # other
        else:
            arg1 = alu_in['rn_val']
            arg2 = alu_in['rm_val']

        f = getattr(self, 'op_' + op)

        return {
            'id': alu_in['id'],
            'rd': alu_in['rd'],
            'keep': (0x000000000000FFFF << (alu_in['shamt_val'] * 16)) ^ 0xFFFFFFFFFFFFFFFF if op == 'movk' else None,
            'value': f(arg1, arg2),
            'assembly': alu_in['assembly']
        }

    @staticmethod
    def op_and(arg1, arg2):
        return arg1 & arg2

    @staticmethod
    def op_add(arg1, arg2):
        return arg1 + arg2

    @staticmethod
    def op_addi(arg1, arg2):
        return ALU.op_add(arg1, arg2)

    @staticmethod
    def op_orr(arg1, arg2):
        return arg1 | arg2

    @staticmethod
    def op_eor(arg1, arg2):
        return arg1 ^ arg2

    @staticmethod
    def op_sub(arg1, arg2):
        return arg1 - arg2

    @staticmethod
    def op_subi(arg1, arg2):
        return ALU.op_sub(arg1, arg2)

    @staticmethod
    def op_asr(arg1, shamt):
        return arg1 >> shamt

    @staticmethod
    def op_lsr(arg1, shamt):
        return (arg1 % (1 << 32)) >> shamt

    @staticmethod
    def op_lsl(arg1, shamt):
        return arg1 << shamt

    @staticmethod
    def op_movz(arg1, shamt):
        return ALU.op_lsl(arg1, shamt * 16)

    @staticmethod
    def op_movk(arg1, shamt):
        return ALU.op_lsl(arg1, shamt * 16)
