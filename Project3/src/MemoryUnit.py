class MemoryUnit:

    def __init__(self, cache):
        self.__cache = cache

    def run(self, mem_in):
        if mem_in['name'] == 'STUR':
            self.__store(mem_in)
        else:
            return {
                'id': mem_in['id'],
                'rn_val': mem_in['rn_val'],
                'rt': mem_in['rt'],
                'value': self.__load(mem_in),
                'assembly': mem_in['assembly'],
                'name': mem_in['name']
            }

    def __store(self, mem_in):
        id = mem_in['id']
        rt_val = mem_in['rt_val']
        offset = mem_in['offset']
        rn_val = mem_in['rn_val']

        return self.__cache.write(rn_val + offset, rt_val, False)

    def __load(self, mem_in):
        id = mem_in['id']
        rn_val = mem_in['rn_val']
        offset = mem_in['offset']
        address = rn_val + offset

        values = self.__cache.read(address)
        return values[0] if address % 8 == 0 else values[1]
