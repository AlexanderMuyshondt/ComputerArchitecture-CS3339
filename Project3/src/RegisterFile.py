class RegisterFile:

    def __init__(self, num_registers=32):
        self.__registers = [0] * num_registers

    def write_register(self, r, val):
        if r is None or val is None:
            pass
        self.__registers[r] = val

    def read_register(self, r):
        return self.__registers[r]
