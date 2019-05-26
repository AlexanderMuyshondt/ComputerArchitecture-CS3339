class Cache:

    def __init__(self, memory):

        self.__cache = (
            {
                'lru': 0,  # 0 or 1
                'blocks': (
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    },
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    }
                )
            },
            {
                'lru': 0,  # 0 or 1
                'blocks': (
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    },
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    }
                )
            },
            {
                'lru': 0,  # 0 or 1
                'blocks': (
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    },
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    }
                )
            },
            {
                'lru': 0,  # 0 or 1
                'blocks': (
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    },
                    {
                        'valid': False,
                        'dirty': False,
                        'tag': 0,
                        'content': (0, 0)
                    }
                )
            }
        )

        self.__memory = memory

    def load(self, address):
        if address % 8 == 0:
            next_address = address + 4
        else:
            next_address = address
            address = next_address - 4

        val1 = self.__memory[address] if address in self.__memory.keys() else 0
        val2 = self.__memory[next_address]if next_address in self.__memory.keys() else 0
        self.write(address, (val1, val2), True)

    def read(self, address):
        address_str = '{0:032b}'.format(address)
        tag = int(address_str[0:27], 2)
        set_index = int(address_str[27:29], 2)

        set = self.__cache[set_index]

        for b, block in enumerate(set['blocks']):
            if tag == block['tag']:
                set['lru'] = b ^ 1
                return block['content']

        # If cache miss, return False
        return False

    def write(self, address, values, is_allocate):
        address_str = '{0:032b}'.format(address)
        tag = int(address_str[0:27], 2)
        set_index = int(address_str[27:29], 2)
        # block_offset = int(address_str[29:30], 2)

        set = self.__cache[set_index]

        block_index = set['lru']
        block = set['blocks'][block_index]

        # If we are allocating, get stuff from memory
        if is_allocate:
            block['valid'] = True
            block['dirty'] = False
            block['tag'] = tag
            block['content'] = values
            set['lru'] ^= 1
            return True

        # If not valid, cache miss so return False
        elif not block['valid']:
            return False
        # If set is full, kick out least recently used and return
        elif self.__is_full(set):

            # If dirty bit set, write to memory
            if block['dirty']:
                self.__memory[address] = block['content'][0]
                self.__memory[address + 4] = block['content'][1]

            # Reset fields
            block['valid'] = False
            block['dirty'] = False
            block['tag'] = None
            block['content'] = (None, None)
            return False
        else:
            block['valid'] = True
            block['dirty'] = True
            block['tag'] = tag
            block['content'] = values
            set['lru'] ^= 1
            return True

    def get_cache(self):
        return self.__cache

    @staticmethod
    def __is_full(set):
        return set['blocks'][0]['valid'] and set['blocks'][1]['valid']
