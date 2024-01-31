from stream import STREAM


class Line:
    def __init__(self, listing, ea):
        self.listing = listing
        self.ea = ea
        self.len = 1
        # 'p' - proc, 'P' - last command of proc
        # 'c' - code
        # 'd' - data (не используется)
        # 'u' - undef, '?' - invalid, '#' - unused
        self.flags = set('u')
        self.instruction = None
        self.args = None        # see disassembler class
        self.name = None
        self.comment = None

    def __str__(self):
        if self.name is not None:
            label = f'{self.name}:\n'
        else:
            label = ''

        f = self.flags.copy()
        mark = []
        mark.append('p') if 'p' in f else mark.append(' ')
        f.discard('p')
        mark.append('c') if 'c' in f else mark.append(' ')
        f.discard('c')
        mark.append('u') if 'u' in f else mark.append(' ')
        f.discard('u')
        f.discard('P')  # Конец ф-ии
        mark = ''.join(mark)
        mark += str(list(f))

        address = f'{self.ea:06X}'
        if self.listing.mem is not None:
            address += f' [{self.ea - self.listing.mem.mem_offset + self.listing.mem.file_offset:04X}]'

        if self.listing.mem and self.listing.mem.is_defined(self.ea, self.len):
            dump = self.listing.mem.get_block(self.ea, self.ea + self.len)
            hex_dump = ''.join((f'{b:02X}' for b in dump))
            if len(hex_dump) > 12:
                hex_dump = f'{hex_dump[0:12]}...'
        else:
            hex_dump = '??'

        command = self.listing.dis.instruction_str(self.instruction, self.args)

        line = f'{mark:<8}{address} {hex_dump:<16}{command}'

        if self.comment is not None:
            # comment = self.comment.replace('\n', '\n'+' '*64+' // ')
            comment = self.comment
            line = f'{line:<64} // {comment}'

        line = label + line

        return line

    def set_comment(self, comment):
        self.comment = comment

    def arg(self, n):
        return self.listing.dis.arg(self.args[n])

    def arg_type(self, n):
        return self.listing.dis.arg_type(self.args[n])

    def arg_str(self, n):
        return self.listing.dis.arg_str(self.args[n])

    def set_arg_type(self, n, new_type):
        self.args[n] = (self.arg(n), new_type)

    def next(self):
        return self.listing.line(self.ea + self.len)


class Listing:
    def __init__(self):
        self.glob = []
        self.lines = {}
        self.mem = None
        self.dis = None
        self.code_start = None
        self.code_end = None

    def __str__(self):
        return '\n'.join(self.generate())

    def set_mem(self, stream: STREAM):
        self.mem = stream

    def line(self, ea, add=False) -> Line:
        if ea in self.lines:
            return self.lines[ea]
        else:
            line = Line(self, ea)
            if add:
                self.lines[ea] = line
            return line

    def flags(self, ea):
        if ea in self.lines:
            return self.lines[ea].flags
        else:
            return set()

    def get_label(self, ea):
        if ea in self.lines:
            return self.lines[ea].name
        else:
            return None

    def set_flags(self, ea, flags: set):
        f = self.line(ea, True).flags
        if 'd' in flags:
            f.discard('c')
            f.discard('u')
        if 'c' in flags:
            f.discard('d')
            f.discard('u')
        if '?' in flags:
            f.discard('u')
        f.update(flags)

    def set_flag_proc(self, ea):
        self.set_flags(ea, set('p'))

    def set_flag_invalid(self, ea):
        self.set_flags(ea, set('?'))

    def set_flag_unused(self, ea):
        self.set_flags(ea, set('#'))

    def set_label(self, ea, name, force=True):
        line = self.line(ea, True)
        if line.name is None or force:
            line.name = name

    def set_command(self, ea, length, instruction, args: list):
        line = self.line(ea, True)
        line.ea = ea
        line.len = length
        line.instruction = instruction
        line.args = args
        self.set_flags(ea, set('c'))

    def set_comment(self, ea, comment):
        self.line(ea, True).comment = comment

    def set_string0(self, ea):
        p = self.mem.pos
        self.mem.pos = ea
        string = self.mem.read_str()
        length = self.mem.pos-ea
        self.set_command(ea, length,  '.DB', [(self.esc_string(string), 's')])
        self.set_label(ea, self.lbl_string(string, ea))
        self.mem.pos = p

    @staticmethod
    def esc_string(string):
        return f'"{repr(string)[1:-1]}"'

    @staticmethod
    def lbl_string(string, ea=None):
        lbl = ''
        for c in string:
            if c == '\n' or c == '\r':
                lbl += '_'
            elif 'A' <= c <= 'Z':
                lbl += chr(ord(c)+0x20)
            elif 'a' <= c <= 'z':
                lbl += c
            elif '0' <= c <= '9':
                lbl += c
            elif c == '-':
                lbl += c
        if len(lbl) == 0:
            lbl = '_'
        elif '0' <= lbl[0] <= '9':
            lbl = '_' + lbl
        # no more than 8 chars
        lbl = lbl[:8]
        if ea is not None:
            lbl += f'_{ea:04X}'

        return lbl

    def get_addresses(self, flags):
        return [a for a in self.lines if self.mem.is_defined(a, 1) and flags <= self.lines[a].flags]

    def disasm_proc(self, ea):
        # disasm proc
        ea_first = ea
        ea_last = ea
        branch = set()
        branch.add(ea)
        while len(branch) != 0:
            a = branch.pop()
            if a < ea_first:
                print('code before start function!')
            if a > ea_last:
                ea_last = a
            if 'c' not in self.flags(a):
                branch.update(self.dis.disasm_command(a))
        # next command - end of function
        if '?' not in self.line(ea_last).flags:
            self.set_flags(self.line(ea_last).next().ea, set('P'))
        else:
            # mark bad function
            self.set_flag_invalid(ea)

        # дизассемблировать неиспользуемый код...
        line = self.line(ea_first)
        while line.ea <= ea_last:
            if 'u' in line.flags:
                self.dis.disasm_command(line.ea)
                line = self.line(line.ea)
                self.set_flag_unused(line.ea)
            line = line.next()

        if self.code_start is None or ea_first < self.code_start:
            self.code_start = ea_first
        if self.code_end is None or ea_last > self.code_end:
            self.code_end = ea_last

    def disassemble(self, disassembler_class, presets=None):
        lst = []
        if presets is None:
            presets = {}

        self.dis = disassembler_class(self, presets)

        # Mark known labels
        for ea, name, comment in presets.get('labels', []):
            self.set_label(ea, name)
            if comment:
                self.set_comment(ea, comment)

        # Mark known procs
        for ea in presets.get('procs', []):
            self.set_flag_proc(ea)

        # дизассемблируем ф-ии начиная с точек входа и далее углубляемся по мере вызова
        # тут в listing точки входа в процедуры и ссылки на глобальные переменные
        while True:
            func_ea = self.get_addresses(set('pu'))
            if len(func_ea) == 0:
                break
            for ea in func_ea:
                self.disasm_proc(ea)

        # попытаемся определить неиспользуемые ф-ии
        # Если первая ф-ия начинается не с начала, то в начале - точно ф-ия
        ea = self.mem.mem_offset
        if self.code_start is not None and ea < self.code_start:
            self.set_label(ea, f'unused_{ea:04X}')
            self.set_flag_proc(ea)
            self.disasm_proc(ea)
        # Всё что между ф-иями - тоже ф-ии
        while True:
            func_ea = [ea for ea in self.get_addresses(set('uP')) if ea < self.code_end]
            if len(func_ea) == 0:
                break
            for ea in func_ea:
                self.set_label(ea, f'unused_{ea:04X}')
                self.set_flag_proc(ea)
                self.disasm_proc(ea)

        # "декомпиляция"
        self.dis.post_process()

        # генерим листинг
        lst.extend(self.generate())
        return lst

    def generate(self):
        lst = self.glob.copy()
        if self.mem is not None:
            a_next = self.line(self.mem.mem_offset)

        for a in sorted(self.lines):
            line = self.line(a)
            if self.mem is not None:
                while a_next.ea < line.ea:
                    lst.append(str(a_next))
                    a_next = a_next.next()

            if 'P' in line.flags:
                lst.append('')  # end of function - add space
                lst.append('')

            lst.append(str(line))
            a_next = line.next()

        if self.mem is not None:
            last_ea = self.mem.mem_offset+self.mem.len
            while a_next.ea < last_ea:
                # ?? if self.mem.is_defined(a, 1):
                lst.append(str(a_next))
                a_next = a_next.next()

        return lst
