from struct import unpack


class MemoryNotDefined(Exception):
    def __init__(self, ea, length, file_offset):
        self.message = f'Error: {length} bytes @{ea:04x}..@{ea+length-1:04x} not defined ({file_offset})'
        super().__init__(self.message)


class STREAM:
    def __init__(self):
        self.bin = None         # bytearray
        self.len = 0
        self.pos = 0            # смещение в bin
        self.mem_offset = 0     # соответсвующее смещение в памяти
        self.file_offset = 0    # соответсвующее смещение в файле

    def set_bin(self, bin, mem_offset=0):
        self.bin = bin
        self.len = len(bin)
        self.pos = mem_offset
        self.mem_offset = mem_offset
        self.file_offset = 0

    def load_bin(self, filename, mem_offset=0):
        with open(filename, 'rb') as f:
            self.set_bin(f.read(), mem_offset)
            f.close()

    def load_hex(self, filename, mem_offset=0):
        with open(filename, 'r') as f:
            content = f.read()
            f.close()
            content = content.replace("\n", "")
            self.set_bin([int(content[i: i+2], 16) for i in range(0, len(content), 2)], mem_offset)

    def get_all(self):
        result = self.bin[0:self.len]
        return result

    def get_block(self, start, end):
        length = end-start
        p = self.__get_abspos(start, length)
        result = self.bin[p:p+length]
        return result

    def is_defined(self, pos, length):
        return False if self.__is_defined(pos, length) is None else True

    def __is_defined(self, pos, length):
        p = pos-self.mem_offset
        if length > 0 and (p < 0 or p > self.len-length):
            return None
        return p

    def __get_abspos(self, pos, length):
        p = self.__is_defined(pos, length)
        if p is None:
            raise MemoryNotDefined(pos, length, p+self.file_offset)
        return p

    def __read(self, fmt, length):
        p = self.__get_abspos(self.pos, length)
        result = unpack(fmt, self.bin[p:p+length])
        self.pos += length
        return result[0]

    def peek_char(self):
        p = self.__get_abspos(self.pos, 1)
        return unpack('c', self.bin[p:p + 1])[0]

    def read_block(self, length):
        p = self.__get_abspos(self.pos, length)
        result = self.bin[p:p+length]
        self.pos += length
        return result

    def read_stream(self, length):
        result = STREAM()
        p = self.__get_abspos(self.pos, length)
        result.set_bin(self.bin[p:p+length])
        result.file_offset = p+self.file_offset
        self.pos += length
        return result

    def read_char(self):
        return self.__read('c', 1)

    def read_byte(self):
        return self.__read('B', 1)

    def read_wordbe(self):
        return self.__read('>H', 2)

    def read_dwordbe(self):
        return self.__read('>I', 4)

    def read_wordle(self):
        return self.__read('<H', 2)

    def read_dwordle(self):
        return self.__read('<I', 4)

    def read_str(self, end=b'\0'):
        result = b''
        while True:
            c = self.read_char()
            if c == end:
                break
            result += c
        return result.decode(encoding='cp1251', errors='ignore')
