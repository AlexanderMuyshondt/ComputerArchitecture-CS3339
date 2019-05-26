from Disassembler import Disassembler


class IFUnit:

    def __init__(self, cache, register_file):
        self.__cache = cache
        self.__register_file = register_file

    def __change_pc(self, inst, pc):
        should_branch = False
        if inst['type'] == 'B':
            should_branch = True
        elif inst['type'] == 'CB':
            if inst['name'] == 'CBZ' and self.__register_file.read_register(inst['rt']) == 0:
                should_branch = True
            elif inst['name'] == 'CBNZ' and self.__register_file.read_register(inst['rt']) != 0:
                should_branch = True

        return (inst['id'] * 4 + 96) + inst['offset'] * 4 if should_branch else pc

    def run(self, pc, num_inst):
        try:
            insts = self.__cache.read(pc)
        except KeyError:
            return False

        if pc % 8 == 4:
            num_inst = 1

        # If cache miss
        if not insts:
            return False
        else:
            if num_inst == 1:
                if insts[0] == Disassembler.break_inst:
                    return False
                elif insts[0] == Disassembler.nop_inst:
                    return (), pc + 4
                else:
                    out = Disassembler.process(insts[0]) if pc % 8 == 0 else Disassembler.process(insts[1])
                    out['id'] = (pc - 96) / 4
                    if out['type'] == 'B' or out['type'] == 'CB':
                        return (), self.__change_pc(out, pc)
                    else:
                        return (out,), pc + 4
            else:
                if insts[0] == Disassembler.break_inst:
                    return False
                if insts[0] == Disassembler.nop_inst:
                    return (), pc + 4

                out1 = Disassembler.process(insts[0])
                out1['id'] = (pc - 96) / 4
                out2 = Disassembler.process(insts[1])
                out2['id'] = (pc - 96) / 4 + 1

                if out1['type'] == 'B' or out1['type'] == 'CB':
                    return (), self.__change_pc(out1, pc)
                elif out2['type'] == 'B' or out2['type'] == 'CB':
                    return (out1,), self.__change_pc(out2, pc)
                elif insts[1] == Disassembler.break_inst:
                    return (out1,), pc + 4
                elif insts[1] == Disassembler.nop_inst:
                    return (out1,), pc + 8
                else:
                    return (out1, out2), pc + 8
