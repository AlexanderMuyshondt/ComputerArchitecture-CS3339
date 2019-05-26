from itertools import chain

class IssueUnit:

    def __init__(self, register_file, pre_issue_buffer, pre_mem_buffer, pre_alu_buffer, post_mem_buffer, post_alu_buffer):
        self.__register_file = register_file
        self.__pre_issue_buffer = pre_issue_buffer
        self.__pre_mem_buffer = pre_mem_buffer
        self.__pre_alu_buffer = pre_alu_buffer
        self.__post_mem_buffer = post_mem_buffer
        self.__post_alu_buffer = post_alu_buffer

    def __issue(self, issue_in):
        type = issue_in['type'].lower()

        if type == 'd':
            return {
                'id': issue_in['id'],
                'rt_val': self.__register_file.read_register(issue_in['rt']),
                'rt': issue_in['rt'],
                'offset': issue_in['offset'],
                'rn_val': self.__register_file.read_register(issue_in['rn']),
                'mem_write': True if issue_in['name'] == 'STUR' else False,
                'assembly': issue_in['assembly'],
                'name': issue_in['name']
            }, 'mem'
        else:
            out = {
                'id': issue_in['id'],
                'op': issue_in['name'],
                'rd': issue_in['rd'],
                'shamt_val': None,
                'rn_val': None,
                'rm_val': None,
                'assembly': issue_in['assembly']
            }
            if type == 'i':
                out['imm_val'] = issue_in['immediate']
                out['rn_val'] = self.__register_file.read_register(issue_in['rn'])
            elif type == 'r':
                out['rm_val'] = self.__register_file.read_register(issue_in['rm'])
                out['rn_val'] = self.__register_file.read_register(issue_in['rn'])
                out['shamt'] = issue_in['shamt']
            elif type == 'im':
                out['imm_val'] = issue_in['immediate']
                out['shamt_val'] = issue_in['shamt']
            return out, 'alu'

    def __check_raw_mem(self, to_issue):
        """
        Checks for RAW hazards between the Pre-Issue buffer and the Pre-Mem buffer.
        :param to_issue: The instruction we are trying to issue.
        :return: True if there is a RAW hazard, false otherwise.
        """
        # Set up sources
        src1 = to_issue['rn']
        src2 = to_issue['rt'] if to_issue['name'] == 'STUR' else None

        for inst in chain(self.__pre_mem_buffer, self.__post_mem_buffer):
            dest = inst['rt'] if inst['name'] == 'LDUR' else None
            if src1 == dest or src2 == dest:
                return True

        return False

    def __check_raw_alu(self, to_issue):
        """
        Checks for RAW hazards between the Pre-Issue buffer and the Pre-ALU buffer.
        :param to_issue: The instruction we are trying to issue.
        :return: True if there is a RAW hazard, false otherwise.
        """
        if to_issue['type'] == 'IM':
            return False

        # Set up sources
        src1 = to_issue['rn']
        src2 = to_issue['rm'] if to_issue['type'] == 'R' else None

        for inst in chain(self.__pre_alu_buffer, self.__post_alu_buffer):
            dest = inst['rd']
            if src1 == dest or src2 == dest:
                return True

        return False

    def run(self, pre_mem_space, pre_alu_space):
        count = 0
        if len(self.__pre_issue_buffer) == 0:
            return
        else:
            i = 0
            while i < len(self.__pre_issue_buffer) and count < 2:
                inst = self.__pre_issue_buffer[i]

                # Check for RAW hazards in Pre-Mem and Pre-ALU
                if inst['type'] == 'D' and self.__check_raw_mem(inst):
                    return
                elif self.__check_raw_alu(inst):
                    return
                else:
                    inst = self.__issue(inst)
                    if pre_alu_space > 0 and inst[1] == 'alu':
                        del self.__pre_issue_buffer[i]
                        self.__pre_alu_buffer.append(inst[0])
                        pre_alu_space -= 1
                        count += 1
                    elif pre_mem_space > 0 and inst[1] == 'mem':
                        del self.__pre_issue_buffer[i]
                        self.__pre_mem_buffer.append(inst[0])
                        pre_mem_space -= 1
                        count += 1
                    else:
                        i += 1
                        continue
