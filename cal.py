from stream import STREAM, MemoryNotDefined
from decode import decode_cal
from listing import Listing


class DisassemblerCAL:
    # arg_type:
    # 'r' - var
    # 's' - str
    # 'c' - UI control id
    # 'B' - byte as hex
    # 'W' - word as hex
    # 'D' - dword as hex
    # 'o' - offset to label
    # 'd' - const data

    # 'R=R     ',      0,    'b',    'b',    'n'
    # 'R=D     ',      1,    'b',    'd',    'n'
    # 'R=C     ',      2,    'b',    'b',    'n'
    # 'C=R     ',      3,    'b',    'b',    'n'
    # 'R+R     ',      4,    'b',    'b',    'n'
    # 'R+D     ',      5,    'b',    'd',    'n'
    # 'R-R     ',      6,    'b',    'b',    'n'
    # 'R-D     ',      7,    'b',    'd',    'n'
    # 'R/R     ',      8,    'b',    'b',    'n'
    # 'R/D     ',      9,    'b',    'd',    'n'
    # 'R%R     ',    0Ah,    'b',    'b',    'n'
    # 'R%D     ',    0Bh,    'b',    'd',    'n'
    # 'R*R     ',    0Ch,    'b',    'b',    'n'
    # 'R*D     ',    0Dh,    'b',    'd',    'n'
    # 'R&R     ',    0Eh,    'b',    'b',    'n'
    # 'R&D     ',    0Fh,    'b',    'd',    'n'
    # 'R|R     ',    10h,    'b',    'b',    'n'
    # 'R|D     ',    11h,    'b',    'd',    'n'
    # 'R^R     ',    12h,    'b',    'b',    'n'
    # 'R^D     ',    13h,    'b',    'd',    'n'
    # 'R>>R    ',    14h,    'b',    'b',    'n'
    # 'R>>D    ',    15h,    'b',    'b',    'n'
    # 'R<<R    ',    16h,    'b',    'b',    'n'
    # 'R<<D    ',    17h,    'b',    'b',    'n'
    # 'JR=R    ',    18h,    'b',    'b',    'l'
    # 'JR!=R   ',    19h,    'b',    'b',    'l'
    # 'JR>R    ',    1Ah,    'b',    'b',    'l'
    # 'JR<R    ',    1Bh,    'b',    'b',    'l'
    # 'JR=>R   ',    1Ch,    'b',    'b',    'l'
    # 'JR<=R   ',    1Dh,    'b',    'b',    'l'
    # 'JMP     ',    1Eh,    'l',    'n',    'n'
    # 'RET     ',    1Fh,    'n',    'n',    'n'
    # '@R=R    ',    20h,    'b',    'b',    'n'
    # '@R=D    ',    21h,    'b',    'b',    'n'
    # 'R=@R    ',    22h,    'b',    'b',    'n'
    # 'R=@D    ',    23h,    'b',    'd',    'n'
    # 'C=D     ',    24h,    'b',    'd',    'n'
    # 'CP=D    ',    25h,    'b',    'd',    'n'
    # 'CP=R    ',    26h,    'b',    'b',    'n'
    # '@D=R    ',    27h,    'd',    'b',    'n'
    # '@D=D    ',    28h,    'd',    'b',    'n'
    # 'R=B     ',    29h,    'b',    'b',    'n'
    # 'R=W     ',    2Ah,    'b',    'w',    'n'
    # 'R+B     ',    2Bh,    'b',    'b',    'n'
    # 'R+W     ',    2Ch,    'b',    'w',    'n'
    # 'R-B     ',    2Dh,    'b',    'b',    'n'
    # 'R-W     ',    2Eh,    'b',    'w',    'n'
    # 'R/B     ',    2Fh,    'b',    'b',    'n'
    # 'R/W     ',    30h,    'b',    'w',    'n'
    # 'R*B     ',    31h,    'b',    'b',    'n'
    # 'R*W     ',    32h,    'b',    'w',    'n'
    # 'R%B     ',    33h,    'b',    'b',    'n'
    # 'R%W     ',    34h,    'b',    'w',    'n'
    # 'S=0     ',    35h,    'b',    'n',    'n'
    # 'S+L     ',    36h,    'b',    'l',    'n'
    # 'S+B     ',    37h,    'b',    'b',    'n'
    # 'S+W     ',    38h,    'b',    'i',    'n'
    # 'S+D     ',    39h,    'b',    'd',    'n'
    # 'S+C     ',    3Ah,    'b',    'b',    'n'
    # 'S+BI    ',    3Bh,    'b',    'b',    'n'
    # 'S+RB    ',    3Ch,    'b',    'b',    'n'
    # 'S+RW    ',    3Dh,    'b',    'b',    'n'
    # 'S+RD    ',    3Eh,    'b',    'b',    'n'
    # 'S+RI    ',    3Fh,    'b',    'b',    'n'
    # 'S+RC    ',    40h,    'b',    'b',    'n'
    # 'S+S     ',    41h,    'b',    'b',    'n'
    # 'L=S     ',    42h,    'b',    'b',    'n'
    # 'S+WI    ',    43h,    'b',    'w',    'n'
    # 'S+DI    ',    44h,    'b',    'd',    'n'
    # 'R&B     ',    45h,    'b',    'b',    'n'
    # 'R&W     ',    46h,    'b',    'w',    'n'
    # 'R|B     ',    47h,    'b',    'b',    'n'
    # 'R|W     ',    48h,    'b',    'w',    'n'
    # 'R^B     ',    49h,    'b',    'b',    'n'
    # 'R^W     ',    4Ah,    'b',    'w',    'n'
    # 'CALL    ',    4Bh,    'l',    'n',    'n'
    # 'R=?R    ',    4Ch,    'b',    'b',    'n'
    # 'R=?D    ',    4Dh,    'b',    'd',    'n'
    # 'S=S     ',    4Eh,    'b',    'b',    'n'
    # 'PRN     ',    4Fh,    'b',    'b',    'n'

    def __init__(self, listing: Listing, presets: dict):
        self.listing = listing
        self.presets = presets

    @staticmethod
    def arg(arg):
        return arg[0]

    @staticmethod
    def arg_type(arg):
        return arg[1]

    def arg_str(self, arg):
        v = self.arg(arg)
        t = self.arg_type(arg)
        if t == 'r':
            # variable
            return f'var{v}'
        if t == 's':
            # string
            return f'str{v}'
        elif t == 'c':
            # ui field
            return self.listing.ui[v]
        if t == 'B':
            # byte
            return f'0x{v:02x}'
        if t == 'W':
            # word
            return f'0x{v:04x}'
        if t == 'D':
            # dword
            return f'0x{v:08x}'
        elif t == 'o':
            o_label = self.listing.get_label(v)
            if o_label is not None:
                return o_label
            else:
                return f'unnamed_{v}'
        else:
            # data (constant)
            return f'{v}'

    def instruction_str(self, instruction, args):
        if instruction is not None:
            # todo: Digit <- dec  |  Hexdigit <- hex
            return instruction.format(*map(self.arg_str, args))
        else:
            return ''

    def decode_string(self, ea):
        p = self.listing.mem.pos
        self.listing.mem.pos = ea
        string = []
        char = self.listing.mem.read_byte() ^ 0x80
        string.append(char)
        key = char
        while True:
            w = self.listing.mem.read_byte() ^ key
            if w == 0:
                break
            string.append(w)
        length = self.listing.mem.pos - ea
        string = bytearray(string).decode('windows-1251')
        self.listing.set_command(ea, length, '// {0}', [(f'{self.listing.esc_string(string)}', 'd')])
        self.listing.mem.pos = p
        return string

    def disasm_command(self, ea):
        addresses = set()

        def set_command(instruction, args):
            self.listing.set_command(ea, self.listing.mem.pos-ea, instruction, args)

        m = self.listing.mem
        m.pos = ea
        do_break = False

        try:
            c = m.read_byte()
            if c == 0x00:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x01:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x02:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 'r'), (t1, 'c')])

            elif c == 0x03:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 'c'), (t1, 'r')])

            elif c == 0x04:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x05:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} + {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x06:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} - {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x07:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} - {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x08:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} / {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x09:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} / {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x0A:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} % {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x0B:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} % {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x0C:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} * {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x0D:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} * {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x0E:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} & {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x0F:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} & {1}', [(t0, 'r'), (t1, 'D')])

            elif c == 0x10:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} | {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x11:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} | {1}', [(t0, 'r'), (t1, 'D')])

            elif c == 0x12:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} ^ {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x13:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} ^ {1}', [(t0, 'r'), (t1, 'D')])

            elif c == 0x14:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} >> {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x15:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} >> {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x14:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} << {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x17:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} << {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x18:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} == {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x19:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} != {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x1A:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} > {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x1B:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} < {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x1C:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} >= {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x1D:
                t0 = m.read_byte()
                t1 = m.read_byte()
                t2 = m.read_word_le()
                label = f'label_{t2:06x}'
                self.listing.set_label(t2, label)
                set_command('if {0} <= {1} goto {2}', [(t0, 'r'), (t1, 'r'), (t2, 'o')])
                addresses.add(t2)

            elif c == 0x1E:
                t0 = m.read_word_le()
                label = f'label_{t0:06x}'
                self.listing.set_label(t0, label)
                set_command('jmp {0}', [(t0, 'o')])
                do_break = True

            elif c == 0x1F:
                set_command('return', [])
                do_break = True

            elif c == 0x20:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('@{0} = {1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x21:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('@{0} = {1}', [(t0, 'r'), (t1, 'B')])

            elif c == 0x22:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = @{1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x23:
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = @{1}', [(t0, 'r'), (t1, 'W')])

            elif c == 0x24:
                # 'C=D     ',    24h,    'b',    'd'
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {1}', [(t0, 'c'), (t1, 'd')])

            elif c == 0x25:
                # 'CP=D    ',    25h,    'b',    'd'
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                t = t1 >> 24
                v = t1 & 0xFFFFFF
                if t == 1:
                    set_command('{0}.Color = {1}', [(t0, 'c'), (v, 'D')])
                elif t == 2:
                    set_command('{0}.Bold = {1}', [(t0, 'c'), (v, 'd')])
                elif t == 3:
                    v = {0: 'left', 2: 'right', 1: 'center'}.get(v, '?')
                    set_command('{0}.Alignment = {1}', [(t0, 'c'), (v, 'd')])

            elif c == 0x26:
                # 'CP=R    ',    26h,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0}.Color = {1}', [(t0, 'c'), (t1, 'r')])
                # Encoding Like 0x25
                self.listing.set_comment(ea, 'Color | Bold | Alignment')

            elif c == 0x27:
                # '@D=R    ',    27h,    'd',    'b'
                t0 = m.read_dword_le()
                t1 = m.read_byte()
                set_command('@{0} = {1}', [(t0, 'W'), (t1, 'r')])

            elif c == 0x28:
                # '@D=D    ',    28h,    'd',    'b'
                t0 = m.read_dword_le()
                t1 = m.read_byte()
                set_command('@{0} = {1}', [(t0, 'W'), (t1, 'B')])

            elif c == 0x29:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2A:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2B:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2C:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} + {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2D:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} - {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2E:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} - {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x2F:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} / {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x30:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} / {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x31:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} * {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x32:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} * {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x33:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} % {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x34:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} % {1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x35:
                t0 = m.read_byte()
                set_command('{0} = ""', [(t0, 's')])

            elif c == 0x36:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                s = self.decode_string(t1)
                set_command('{0} = {0} + "{1}"', [(t0, 's'), (s, 'd')])

            elif c == 0x37:
                # 'S+B     ',    37h,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #b.{1}', [(t0, 's'), (t1, 'B')])

            elif c == 0x38:
                # 'S+W     ',    38h,    'b',    'i'
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} + #w.{1}', [(t0, 's'), (t1, 'W')])

            elif c == 0x39:
                # 'S+D     ',    39h,    'b',    'd'
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = {0} + #d.{1}', [(t0, 's'), (t1, 'D')])

            elif c == 0x3A:
                # 'S+C     ',    3Ah,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #c.{1}', [(t0, 's'), (t1, 'B')])

            elif c == 0x3B:
                # 'S+BI    ',    3Bh,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #i.{1}', [(t0, 's'), (t1, 'd')])

            elif c == 0x3C:
                # 'S+RB    ',    3Ch,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #b.{1}', [(t0, 's'), (t1, 'r')])

            elif c == 0x3D:
                # 'S+RW    ',    3Dh,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #w.{1}', [(t0, 's'), (t1, 'r')])

            elif c == 0x3E:
                # 'S+RD    ',    3Eh,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #d.{1}', [(t0, 's'), (t1, 'r')])

            elif c == 0x3F:
                # 'S+RI    ',    3Fh,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #i.{1}', [(t0, 's'), (t1, 'r')])

            elif c == 0x40:
                # 'S+RC    ',    40h,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + #c.{1}', [(t0, 's'), (t1, 'r')])

            elif c == 0x41:
                # 'S+S     ',    41h,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} + {1}', [(t0, 's'), (t1, 's')])

            elif c == 0x42:
                # 'L=S     ',    42h,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 'c'), (t1, 's')])

            elif c == 0x43:
                # 'S+WI    ',    43h,    'b',    'w'
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('??{0} = {0} + {1}', [(t0, 's'), (t1, 'D')])

            elif c == 0x44:
                # 'S+DI    ',    44h,    'b',    'd'
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('??{0} = {0} + {1}', [(t0, 's'), (t1, 'D')])

            elif c == 0x45:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} & {1}', [(t0, 'r'), (t1, 'B')])

            elif c == 0x46:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} & {1}', [(t0, 'r'), (t1, 'W')])

            elif c == 0x47:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} | {1}', [(t0, 'r'), (t1, 'B')])

            elif c == 0x48:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} | {1}', [(t0, 'r'), (t1, 'W')])

            elif c == 0x49:
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {0} ^ {1}', [(t0, 'r'), (t1, 'B')])

            elif c == 0x4a:
                t0 = m.read_byte()
                t1 = m.read_word_le()
                set_command('{0} = {0} ^ {1}', [(t0, 'r'), (t1, 'W')])

            elif c == 0x4b:
                # 'CALL    ',    4Bh,    'l'
                t0 = m.read_word_le()
                label = f'proc_{t0:06x}'
                self.listing.set_label(t0, label)
                self.listing.set_flag_proc(t0)
                set_command('call {0}', [(t0, 'o')])

            elif c == 0x4c:
                # 'R=?R    ',    4Ch,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = ?{1}', [(t0, 'r'), (t1, 'r')])

            elif c == 0x4d:
                # 'R=?D    ',    4Dh,    'b',    'd'
                t0 = m.read_byte()
                t1 = m.read_dword_le()
                set_command('{0} = ?{1}', [(t0, 'r'), (t1, 'd')])

            elif c == 0x4e:
                # 'S=S     ',    4Eh,    'b',    'b'
                t0 = m.read_byte()
                t1 = m.read_byte()
                set_command('{0} = {1}', [(t0, 's'), (t1, 's')])

            elif c == 0x4f:
                # 'PRN     ',    4Fh,    'b',    'b'
                t0 = m.read_byte()
                set_command('print {0}', [(t0, 'r')])

            else:
                # invalid instruction
                self.listing.set_flag_invalid(ea)
                do_break = True

            if not do_break:
                addresses.add(m.pos)

        except MemoryNotDefined as e:
            print(hex(ea), e)

        return addresses

    def post_process(self):
        pass


class CAL:
    def __init__(self, filename):
        self.listing = None
        self.ui = {}
        self.window_listing = []
        self.script_listing = []
        self.stream = STREAM()
        self.data = STREAM()
        try:
            self.stream.load_hex(filename)
        except ValueError:
            print('Probably file as source code')

    def get_lst(self):
        lst = []
        lst.extend(self.window_listing)
        lst.extend(self.script_listing)
        return lst

    def get_data(self):
        return self.data.get_all()

    def read_str(self, key):
        text = []
        while True:
            b = key ^ self.data.read_byte()
            key += 1
            if b == 0:
                break
            text.append(b)
        return bytearray(text).decode('windows-1251')

    def decompile_window(self):
        code = []
        width = self.data.read_word_le()
        height = self.data.read_word_le()
        code.append(f'Size({width}, {height});')
        code.append('Form')
        code.append('{')
        tabwidth = 4
        pad = tabwidth
        ctrl_id = 0
        while True:
            c = self.data.read_byte()
            if chr(c) == 'G':
                # Group
                text = self.read_str(c)
                left = self.data.read_word_le()
                top = self.data.read_word_le()
                width = self.data.read_word_le()
                height = self.data.read_word_le()
                code.append(f'{" " * pad}Group("{text}", {left}, {top}, {width}, {height})')
                code.append(f'{" " * pad}{{')
                pad += tabwidth

            elif chr(c) == 'L':
                # Label
                text = self.read_str(c)
                left = self.data.read_word_le()
                top = self.data.read_word_le()
                name = f'label_{ctrl_id}'
                self.ui[ctrl_id] = name
                ctrl_id += 1
                code.append(f'{" " * pad}Label({name}, "{text}", {left}, {top});')
            elif chr(c) == 'P':
                # Picture
                text = self.read_str(c)
                left = self.data.read_word_le()
                top = self.data.read_word_le()
                width = self.data.read_word_le()
                height = self.data.read_word_le()
                name = f'pict_{ctrl_id}'
                self.ui[ctrl_id] = name
                ctrl_id += 1
                code.append(f'{" " * pad}Picture({name}, "{text}", {left}, {top}, {width}, {height});')
            elif chr(c) == 'H':
                # Hexdigit
                text = self.read_str(c)
                left = self.data.read_word_le()
                top = self.data.read_word_le()
                width = self.data.read_word_le()
                s = self.data.read_word_le()
                name = f'hex_{ctrl_id}'
                self.ui[ctrl_id] = name
                ctrl_id += 1
                code.append(f'{" " * pad}HexDigit({name}, "{text}", {left}, {top}, {width}, {s});')
            elif chr(c) == 'T':
                # Text
                code.append('!!!B')
            elif chr(c) == 'B':
                # Checkbox
                code.append('!!!B')
            elif chr(c) == 'C':
                # Combobox
                code.append('!!!C')
            elif chr(c) == 'D':
                # Digit
                text = self.read_str(c)
                left = self.data.read_word_le()
                top = self.data.read_word_le()
                width = self.data.read_word_le()
                name = f'digit_{ctrl_id}'
                self.ui[ctrl_id] = name
                ctrl_id += 1
                code.append(f'{" " * pad}Digit({name}, "{text}", {left}, {top}, {width});')
            elif chr(c) == 'g':
                #
                pad -= tabwidth
                code.append(f'{" " * pad}}}')
            elif c == 0xFF:
                # End of form
                break
            else:
                code.append(f'Unknown {c}')
        code.append('}')
        code.append('')
        self.window_listing = code

    def decompile(self):
        if self.stream.len == 0:
            return
        code = []

        self.data.set_binary(decode_cal(self.stream.bin))
        self.listing = Listing()
        self.listing.ui = self.ui

        on_show = self.data.read_word_le()    # 0 After load
        on_apply = self.data.read_word_le()   # 1 Button Click
        on_select = self.data.read_word_le()  # 2 Select hexdump range
        unused = self.data.read_word_le()
        if on_show != 0xFFFF:
            self.listing.set_label(on_show, 'OnShow')
            self.listing.set_flag_proc(on_show)
        else:
            code.append('// OnShow don\'t used')
        if on_apply != 0xFFFF:
            self.listing.set_label(on_apply, 'OnApply')
            self.listing.set_flag_proc(on_apply)
        else:
            code.append('// OnApply don\'t used')
        if on_select != 0xFFFF:
            self.listing.set_label(on_select, 'OnChange')
            self.listing.set_flag_proc(on_select)
        else:
            code.append('// OnSelect don\'t used')
        code.append(f'// unused field = {unused}')

        self.decompile_window()

        bytecode = self.data.read_stream(self.data.len-self.data.pos)
        bytecode.mem_offset = bytecode.file_offset
        self.listing.set_mem(bytecode)
        code.extend(self.listing.disassemble(DisassemblerCAL))
        self.script_listing = code
