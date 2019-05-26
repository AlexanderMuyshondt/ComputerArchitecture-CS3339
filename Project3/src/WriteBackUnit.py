class WriteBackUnit:

    def __init__(self, register_file):
        self.__register_file = register_file

    def run(self, wb_in, source):

        if source == 'mem':
            id = wb_in['id']
            dest = wb_in['rt']
            value = wb_in['value']
            self.__register_file.write_register(dest, value)

        else:
            id = wb_in['id']
            dest = wb_in['rd']
            value = wb_in['value']

            if wb_in['keep']:
                curr = self.__register_file.read_register(dest)
                value = (curr & wb_in['keep']) | value
                self.__register_file.write_register(dest, value)
            else:
                self.__register_file.write_register(dest, value)

