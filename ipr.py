import decode
from stream import STREAM, MemoryNotDefined
from decode import Decoder
from listing import Listing
from ipr_decomp import IPRDecomp


class DisassemblerIPR:
    # arg_type:
    # 'r' - register
    # 'd' - const data
    # 'o' - offset
    # 'a' - offset to array

    # instruction argument types
    # A - Address
    # B - Byte
    # W - Word
    # D - Dword
    # T - Half byte
    # R - Register
    # N - None
    # noinspection SpellCheckingInspection
    mnemonics = {
        0x00: ['MOV', 'RRN'],
        0x01: ['LDB', 'RBN'],
        0x02: ['LDW', 'RWN'],
        0x03: ['LDD', 'RDN'],
        0x04: ['LDMB', 'RAN'],
        0x05: ['LDMW', 'RAN'],
        0x06: ['LDMD', 'RAN'],
        0x07: ['LDIB', 'RRN'],
        0x08: ['LDIW', 'RRN'],
        0x09: ['LDID', 'RRN'],
        0x0A: ['STMB', 'ARN'],
        0x0B: ['STMW', 'ARN'],
        0x0C: ['STMD', 'ARN'],
        0x0D: ['STIB', 'RRN'],
        0x0E: ['STIW', 'RRN'],
        0x0F: ['STID', 'RRN'],
        0x10: ['ADD', 'RRN'],
        0x11: ['ADDB', 'RBN'],
        0x12: ['ADDW', 'RWN'],
        0x13: ['ADDD', 'RDN'],
        0x14: ['ADDMB', 'RAN'],
        0x15: ['ADDMW', 'RAN'],
        0x16: ['ADDMD', 'RAN'],
        0x17: ['AND', 'RRN'],
        0x18: ['ANDB', 'RBN'],
        0x19: ['ANDW', 'RWN'],
        0x1A: ['ANDD', 'RDN'],
        0x1B: ['ANDMB', 'RAN'],
        0x1C: ['ANDMW', 'RAN'],
        0x1D: ['ANDMD', 'RAN'],
        0x1E: ['SUB', 'RRN'],
        0x1F: ['SUBB', 'RBN'],
        0x20: ['SUBW', 'RWN'],
        0x21: ['SUBD', 'RDN'],
        0x22: ['SUBMB', 'RAN'],
        0x23: ['SUBMW', 'RAN'],
        0x24: ['SUBMD', 'RAN'],
        0x25: ['OR', 'RRN'],
        0x26: ['ORB', 'RBN'],
        0x27: ['ORW', 'RWN'],
        0x28: ['ORD', 'RDN'],
        0x29: ['ORMB', 'RAN'],
        0x2A: ['ORMW', 'RAN'],
        0x2B: ['ORMD', 'RAN'],
        0x2C: ['XOR', 'RRN'],
        0x2D: ['XORB', 'RBN'],
        0x2E: ['XORW', 'RWN'],
        0x2F: ['XORD', 'RDN'],
        0x30: ['XORMB', 'RAN'],
        0x31: ['XORMW', 'RAN'],
        0x32: ['XORMD', 'RAN'],
        0x33: ['MUL', 'RRN'],
        0x34: ['MULB', 'RBN'],
        0x35: ['MULW', 'RWN'],
        0x36: ['MULD', 'RDN'],
        0x37: ['MULMB', 'RAN'],
        0x38: ['MULMW', 'RAN'],
        0x39: ['MULMD', 'RAN'],
        0x3A: ['DIV', 'RRN'],
        0x3B: ['DIVB', 'RBN'],
        0x3C: ['DIVW', 'RWN'],
        0x3D: ['DIVD', 'RDN'],
        0x3E: ['DIVMB', 'RAN'],
        0x3F: ['DIVMW', 'RAN'],
        0x40: ['DIVMD', 'RAN'],
        0x41: ['MOD', 'RRN'],
        0x42: ['MODB', 'RBN'],
        0x43: ['MODW', 'RWN'],
        0x44: ['MODD', 'RDN'],
        0x45: ['MODMB', 'RAN'],
        0x46: ['MODMW', 'RAN'],
        0x47: ['MODMD', 'RAN'],
        0x48: ['RL', 'RRN'],
        0x49: ['RL', 'RBN'],
        0x4A: ['RR', 'RRN'],
        0x4B: ['RR', 'RBN'],
        0x4C: ['STEM', 'BRR'],
        0x4D: ['LDEM', 'RBR'],
        0x4E: ['IN', 'RBN'],
        0x4F: ['OUT', 'BRN'],
        0x50: ['CMPJE', 'RRA'],
        0x51: ['CMPJNE', 'RRA'],
        0x52: ['CMPJGE', 'RRA'],
        0x53: ['CMPJLE', 'RRA'],
        0x54: ['CMPJL', 'RRA'],
        0x55: ['CMPJG', 'RRA'],
        0x56: ['JMP', 'ANN'],
        0x57: ['CALL', 'ANN'],
        0x58: ['RET', 'BNN'],
        0x59: ['PUSH', 'RNN'],
        0x5A: ['PUSHR', 'BNN'],
        0x5B: ['POPR', 'BNN'],
        0x5C: ['SYS', 'BNN'],
        0x5D: ['ORPI', 'BBN'],
        0x5E: ['ANDPI', 'BBN'],
        0x5F: ['ENTER', 'TTN'],
        0x60: ['JBRS', 'RBA'],
        0x61: ['JBRC', 'RBA'],
        0x62: ['DCALL', 'BNN'],
        0x63: ['JZ', 'RAN'],
        0x64: ['JNZ', 'RAN'],
        0x65: ['CPIJE', 'RBA'],
        0x66: ['CPIJNE', 'RBA'],
        0x67: ['JNZIO', 'BAN'],
        0x68: ['JZIO', 'BAN'],
        0x69: ['LMA', 'RRA'],
        0x6A: ['AWRB', 'RAR'],
        0x6B: ['AWRW', 'RAR'],
        0x6C: ['AWRD', 'RAR'],
        0x6D: ['ARDB', 'RAR'],
        0x6E: ['ARDW', 'RAR'],
        0x6F: ['ARDD', 'RAR'],
        0x70: ['PUSHB', 'BNN'],
        0x71: ['EOUT', 'RRN'],
        0x72: ['EIN', 'RRN'],
    }

    def __init__(self, listing: Listing, presets: dict):
        self.listing = listing
        self.presets = presets

    def is_host(self):
        is_device = self.presets.get('type') == 'device'
        return not is_device

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
            # register
            return f'R{v}'
        elif t == 'o' or t == 'a':
            # offset
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
            a = []
            i = 0
            while i < len(args):
                if self.arg_type(args[i]) == 'a':
                    a.append(self.arg_str(args[i]) + ' + ' + self.arg_str(args[i + 1]))
                    i += 2
                else:
                    a.append(self.arg_str(args[i]))
                    i += 1
            a = ', '.join(a)
            return f'{instruction:<8}{a}'
        else:
            return ''

    def disasm_command(self, ea: int):
        """
        Дизассемблируем 1 инструкцию.
        :param ea: Адрес инструкции.
        :return: Возвращаем адреса, с которых можно продолжать
        """

        def set_command(instruction, args):
            self.listing.set_command(ea, self.listing.mem.pos - ea, instruction, args)

        addresses = set()
        m = self.listing.mem
        m.pos = ea
        do_break = False

        try:
            c = m.read_byte()
            mnem = self.mnemonics.get(c)
            if mnem is not None:
                # noinspection SpellCheckingInspection
                if mnem[1] == 'NNN':  # NNN ?
                    pass
                elif mnem[1] == 'RRN':
                    # MOV, LDIx, STIx, ADD, AND, SUB, OR, XOR, MUL, DIV, MOD, RL, RR, EOUT, EIN
                    a = m.read_byte()
                    t1 = a & 0x0f
                    t2 = a >> 4
                    set_command(mnem[0], [(t1, 'r'), (t2, 'r')])

                elif mnem[1] == 'RBN':
                    # LDB, ADDB, ANDB, SUBB, ORB, XORB, MULB, DIVB, MODB, RL, RR, IN
                    t1 = m.read_byte()
                    t2 = m.read_byte()
                    set_command(mnem[0], [(t1, 'r'), (t2, 'd')])

                elif mnem[1] == 'RWN':
                    # LDW, ADDW, ANDW, SUBW, ORW, XORW, MULW, DIVW, MODW
                    t1 = m.read_byte()
                    t2 = m.read_word_be()
                    # t2 может быть и ссылкой и числом
                    set_command(mnem[0], [(t1, 'r'), (t2, 'd')])

                elif mnem[1] == 'RDN':
                    # LDD, ADDD, ANDD, SUBD, ORD, XORD, MULD, DIVD, MODD
                    t1 = m.read_byte()
                    t2 = m.read_dword_be()
                    set_command(mnem[0], [(t1, 'r'), (t2, 'd')])

                elif mnem[1] == 'RAN':
                    t1 = m.read_byte()
                    t2 = m.read_word_be()
                    set_command(mnem[0], [(t1, 'r'), (t2, 'o')])
                    if mnem[0] in ('JZ', 'JNZ'):
                        # JZ, JNZ
                        addresses.add(t2)
                        self.listing.set_label(t2, f'loc_{t2:04X}', False)
                    else:
                        # LDMx, ADDMx, ANDMx, SUBMx, ORMx, XORMx, MULMx, DIVMx, MODMx
                        pref = 'b_' if mnem[0][-1] == 'B' else 'w_' if mnem[0][-1] == 'W' else 'd_'
                        self.listing.set_label(t2, f'{pref}{t2:04X}', False)

                elif mnem[1] == 'ARN':
                    # STMx
                    t1 = m.read_byte()
                    t2 = m.read_word_be()
                    set_command(mnem[0], [(t2, 'o'), (t1, 'r')])
                    pref = 'b_' if mnem[0][-1] == 'B' else 'w_' if mnem[0][-1] == 'W' else 'd_'
                    self.listing.set_label(t2, f'{pref}{t2:04X}', False)

                elif mnem[1] == 'WNN' or mnem[1] == 'ANN':
                    # JMP, CALL
                    t1 = m.read_word_be()
                    set_command(mnem[0], [(t1, 'o')])
                    # если CALL, то добавить в listing 'p', но не добавляем в addresses
                    if mnem[0] == 'CALL':
                        # CALL
                        # Don't use the proc_ prefix. This conflicts with iProg compiler
                        self.listing.set_label(t1, f'prc_{t1:04X}', False)
                        self.listing.set_flag_proc(t1)

                    else:
                        # JMP
                        addresses.add(t1)
                        self.listing.set_label(t1, f'loc_{t1:04X}', False)

                elif mnem[1] == 'BBN':
                    # ORPI, ANDPI
                    t1 = m.read_byte()
                    t2 = m.read_byte()
                    set_command(mnem[0], [(t1, 'd'), (t2, 'd')])

                elif mnem[1] == 'RRA':
                    # CMPJxx, LMA
                    a = m.read_byte()
                    t1 = a & 0x0f
                    t2 = a >> 4
                    t3 = m.read_word_be()
                    if mnem[0] != 'LMA':
                        set_command(mnem[0], [(t1, 'r'), (t2, 'r'), (t3, 'o')])
                        self.listing.set_label(t3, f'loc_{t3:04X}', False)
                        addresses.add(t3)
                    else:
                        set_command(mnem[0], [(t1, 'r'), (t2, 'r'), (t3, 'd')])

                elif mnem[1] == 'BNN':
                    # RET, PUSHR, POPR, SYS, DCALL, PUSHB
                    t1 = m.read_byte()
                    set_command(mnem[0], [(t1, 'd')])

                elif mnem[1] == 'RNN':
                    # PUSH
                    t1 = m.read_byte()
                    set_command(mnem[0], [(t1, 'r')])

                elif mnem[1] == 'TTN':
                    # ENTER
                    a = m.read_byte()
                    t1 = a & 0x0f
                    t2 = a >> 4
                    set_command(mnem[0], [(t1, 'd'), (t2, 'd')])

                elif mnem[1] == 'BRN':
                    # OUT
                    t1 = m.read_byte()
                    t2 = m.read_byte()
                    set_command(mnem[0], [(t1, 'd'), (t2, 'r')])

                elif mnem[1] == 'RBA':
                    # JBRS, JBRC, CPIJE, CPIJNE
                    t1 = m.read_byte()
                    t2 = m.read_byte()
                    t3 = m.read_word_be()
                    set_command(mnem[0], [(t1, 'r'), (t2, 'd'), (t3, 'o')])
                    self.listing.set_label(t3, f'loc_{t3:04X}', False)
                    addresses.add(t3)

                elif mnem[1] == 'BAN':
                    # JNZIO, JZIO
                    t1 = m.read_byte()
                    t2 = m.read_word_be()
                    set_command(mnem[0], [(t1, 'd'), (t2, 'o')])
                    self.listing.set_label(t2, f'loc_{t2:04X}', False)
                    addresses.add(t2)

                elif mnem[1] == 'BRR':
                    # STEM
                    t1 = m.read_byte()
                    a = m.read_byte()
                    t2 = a & 0x0f
                    t3 = a >> 4
                    set_command(mnem[0], [(t1, 'd'), (t2, 'r'), (t3, 'r')])

                elif mnem[1] == 'RBR':
                    # LDEM
                    t1 = m.read_byte()
                    a = m.read_byte()
                    t2 = a & 0x0f
                    t3 = a >> 4
                    set_command(mnem[0], [(t1, 'd'), (t2, 'r'), (t3, 'r')])

                elif mnem[1] == 'RAR':
                    # AWRx, ARDx
                    a = m.read_byte()
                    t1 = m.read_word_be()
                    t2 = a & 0x0f
                    t3 = a >> 4
                    pref = 'b_' if mnem[0][-1] == 'B' else 'w_' if mnem[0][-1] == 'W' else 'd_'
                    if mnem[0][:3] == 'AWR':
                        # AWRx    t1 + R t2, R t3
                        set_command(mnem[0], [(t1, 'a'), (t2, 'r'), (t3, 'r')])
                    else:
                        # ARDx    R t2, t1 + R t3
                        set_command(mnem[0], [(t2, 'r'), (t1, 'a'), (t3, 'r')])
                    label = f'{pref}{t1:04X}'
                    self.listing.set_label(t1, label, False)

                else:
                    # invalid instruction
                    do_break = True

            else:
                print(f'invalid code {c:x} @{ea:04x}')
                # mark bad instruction
                set_command('<invalid>', [])
                self.listing.set_flag_invalid(ea)
                do_break = True

            if c == 0x58 or c == 0x56:  # RET or JMP
                do_break = True

            if not do_break:
                addresses.add(m.pos)

        except MemoryNotDefined as e:
            print(hex(ea), e)
            # mark bad instruction
            set_command('<invalid>', [])
            self.listing.set_flag_invalid(ea)

        return addresses

    def post_process(self):
        d = IPRDecomp(self.listing)
        func_ea = self.listing.get_addresses(set('pc'))
        for f in func_ea:
            d.decompile(f)
        d.post()


class IPR:
    def __init__(self, filename):
        self.host_listing = None
        self.device_listing = None

        self.b_menu_start = 0
        self.b_menu_end = 0
        self.b_menu_listing = []
        self.b_toolbar_start = 0
        self.b_toolbar_end = 0
        self.b_toolbar_listing = []
        self.b_editor_start = 0
        self.b_editor_end = 0
        self.b_editor_listing = []

        self.b_window_start = 0
        self.b_window_end = 0
        self.b_windows_listing = []

        self.b_host_script_start = 0
        self.b_host_script_end = 0
        self.b_device_script_ep_start = 0
        self.b_device_script_ep_end = 0
        self.b_device_script_crypt_start = 0
        self.b_device_script_crypt_end = 0
        self.b_device_script_crc_start = 0
        self.b_device_script_crc_end = 0
        self.script_listing = []
        self.device_script = None

        self.stream = STREAM()
        self.stream.load_binary(filename)

    def get_lst(self):
        lst = []
        lst.extend(self.b_menu_listing)
        lst.extend(self.b_toolbar_listing)
        lst.extend(self.b_editor_listing)
        lst.extend(self.b_windows_listing)
        lst.extend(self.script_listing)
        return lst

    def get_ipr(self):
        if self.device_script is None:
            return None

        ipr = []
        ipr.extend(self.stream.get_block(self.b_menu_start, self.b_menu_end))
        ipr.extend(self.stream.get_block(self.b_toolbar_start, self.b_toolbar_end))
        ipr.extend(self.stream.get_block(self.b_editor_start, self.b_editor_end))
        ipr.extend(self.stream.get_block(self.b_window_start, self.b_window_end))
        ipr.extend(self.stream.get_block(self.b_host_script_start, self.b_host_script_end))
        ipr.extend(self.stream.get_block(self.b_device_script_ep_start, self.b_device_script_ep_end))

        # Исходные данные, могут быть кодированными
        # ipr.extend(self.stream.get_block(self.b_device_script_crypt_start, self.b_device_script_crypt_end))
        # ipr.extend(self.stream.get_block(self.b_device_script_crc_start, self.b_device_script_crc_end))

        # раскодированные данные
        data = self.device_script.get_all()
        ipr.extend(data)
        crc = decode.crc16(data)
        ipr.append(crc >> 8)
        ipr.append(crc & 0xFF)

        return bytes(ipr)

    def decompile_menu(self):
        start = self.stream.pos
        code = []
        c = self.stream.read_char()
        if c == b'M':
            code.append('Menu')
            while True:
                name = self.stream.read_str(b'\r')
                if name != '-':
                    proc_id = self.stream.read_word_be()
                    menu_id = self.stream.read_byte()       # byte or -1
                    hotkey = self.stream.read_str(b'\r')
                    label = f'{name.replace(" ", "_").replace("&", "")}'
                    if menu_id == 0xFF:
                        menu_id = ''
                    self.host_listing.set_label(proc_id, label)
                    self.host_listing.set_flag_proc(proc_id)
                    code.append(f'    {name},{label},{menu_id},{hotkey}')
                else:
                    code.append('    -')
                if self.stream.peek_char() == b'\0':
                    self.stream.read_char()
                    break
            code.append('EndMenu')
        elif c == b'm':
            # code.append('// is no menu')
            pass
        else:
            raise SyntaxError('Menu section not exists')
        code.append('')
        self.b_menu_start = start
        self.b_menu_end = self.stream.pos
        self.b_menu_listing = code

    def decompile_toolbar(self):
        start = self.stream.pos
        code = []
        c = self.stream.read_char()
        if c == b'T':
            # code.append('// toolbar is visible')
            pass
        elif c == b't':
            code.append('TOOLBAROFF')
        else:
            raise SyntaxError('T section not exists')
        self.b_toolbar_start = start
        self.b_toolbar_end = self.stream.pos
        self.b_toolbar_listing = code

    def decompile_editor(self):
        start = self.stream.pos
        code = []
        c = self.stream.read_char()
        if c == b'E':
            code.append('')
            code.append('Editor')
            code.append('{')
            n = int(self.stream.read_char())    # '1' или '2'
            for n in range(0, n):
                caption = self.stream.read_str(b'\r')
                size = self.stream.read_dword_be()
                mode = self.stream.read_byte()
                b = self.stream.read_byte()
                code.append(f'    (Caption="{caption}";size={size};mode={mode};bytes={b})')
            code.append('}')
        elif c == b'e':
            print('is no Editor')
        else:
            raise SyntaxError('Editor section not exists')
        code.append('')
        self.b_editor_start = start
        self.b_editor_end = self.stream.pos
        self.b_editor_listing = code

    def decompile_window(self):

        def join_fields(fields):
            return '; '.join(f'{k}={v}' for k, v in fields.items())

        start = self.stream.pos
        code = []
        tabwidth = 4
        pad = 0
        c = self.stream.read_char()
        if c == b'W':
            # _ = self.stream.read_char()   # must be /r
            caption = self.stream.read_str(b'\r')

            width = self.stream.read_word_be()
            height = self.stream.read_word_be()
            align = self.stream.read_word_be()
            align = 'h' if align == 0 else 'v'  # ALIGN: Horizontal==0 Vertical==1
            f = {
                'caption': f'"{caption}"',
                'width': width,
                'height': height,
                'align': align
            }
            code.append(f'Window({join_fields(f)})')
            code.append('{')
            pad += tabwidth

            while True:
                t = self.stream.read_char()
                if t == b'\0':
                    break

                elif t == b'g':
                    # Group end
                    pad -= tabwidth
                    code.append(f'{" "*pad}}}')

                elif t == b'G':
                    # Group
                    caption = self.stream.read_str(b'\r')
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    height = self.stream.read_word_be()
                    f = {
                        'caption': f'"{caption}"',
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height
                    }
                    code.append(f'{" "*pad}Group({join_fields(f)})')
                    code.append(f'{" "*pad}{{')
                    pad += tabwidth

                elif t == b'B':
                    # Button
                    caption = self.stream.read_str(b'\r')
                    proc = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    height = self.stream.read_word_be()
                    f = {
                        'caption': f'"{caption}"',
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height
                    }
                    if proc != 0xFFFF:
                        label = f'button_{proc:04X}'
                        # The procname may already be declared in the menu
                        self.host_listing.set_label(proc, label, False)
                        label = self.host_listing.get_label(proc)
                        self.host_listing.set_flag_proc(proc)
                        f['proc'] = label
                    code.append(f'{" "*pad}Button({join_fields(f)})')

                elif t == b'x':
                    # Picture
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    height = self.stream.read_word_be()
                    name = f'picture_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height
                    }
                    code.append(f'{" "*pad}Picture({join_fields(f)})')

                elif t == b'H':
                    # Checkbox
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    proc = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    value = self.stream.read_word_be()
                    name = f'checkbox_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'value': value,
                    }
                    if proc != 0xFFFF:
                        label = f'checkbox_{proc:04X}'
                        self.host_listing.set_label(proc, label)
                        self.host_listing.set_flag_proc(proc)
                        f['proc'] = label
                    code.append(f'{" "*pad}Checkbox({join_fields(f)})')
                    self.host_listing.set_label(name_id, name)

                elif t == b'I':
                    # List
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    proc = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    value = self.stream.read_word_be()
                    items = []
                    while True:
                        c = self.stream.peek_char()
                        if c == b'\0':
                            self.stream.read_char()
                            break
                        items.append(self.stream.read_str(b'\r'))
                    items = ",".join([f'"{i}"' for i in items])
                    name = f'list_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'value': value,
                        'items': items
                    }
                    if proc != 0xFFFF:
                        label = f'list_{proc:04X}'
                        self.host_listing.set_label(proc, label)
                        self.host_listing.set_flag_proc(proc)
                        f['proc'] = label
                    self.host_listing.set_label(name_id, name)
                    code.append(f'{" "*pad}List({join_fields(f)})')

                elif t == b'L':
                    # Label
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    value = self.stream.read_word_be()
                    name = f'label_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'value': value
                    }
                    code.append(f'{" "*pad}Label({join_fields(f)})')

                elif t == b'D':
                    # Digit
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    value = self.stream.read_dword_be()
                    name = f'digit_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'value': value
                    }
                    code.append(f'{" "*pad}Digit({join_fields(f)})')
                    self.host_listing.set_label(name_id, name)

                elif t == b'h':
                    # Hexedit
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    value = self.stream.read_dword_be()
                    name = f'hexedit_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'value': value
                    }
                    code.append(f'{" "*pad}Hexedit({join_fields(f)})')
                    self.host_listing.set_label(name_id, name)

                elif t == b'b':
                    # Hexbytes
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    value = self.stream.read_dword_be()
                    items = ' '.join([f'{self.stream.read_byte():02X}' for _ in range(value)])
                    name = f'hexbytes_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'value': value,
                        'items': f'"{items}"'
                    }
                    code.append(f'{" "*pad}Hexbytes({join_fields(f)})')
                    self.host_listing.set_label(name_id, f'{name}')
                    for i in range(1, value):
                        self.host_listing.set_label(name_id + i, f'{name}[{i}]')

                elif t == b'Y':
                    # Text
                    caption = self.stream.read_str(b'\r')
                    name_id = self.stream.read_word_be()
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    items = self.stream.read_str(b'\r')
                    name = f'text_{name_id:04X}'
                    f = {
                        'caption': f'"{caption}"',
                        'name': name,
                        'left': left,
                        'top': top,
                        'width': width,
                        'items': f'"{items}"'
                    }
                    code.append(f'{" "*pad}Text({join_fields(f)})')

                elif t == b'P':
                    # Pages
                    left = self.stream.read_word_be()
                    top = self.stream.read_word_be()
                    width = self.stream.read_word_be()
                    height = self.stream.read_word_be()
                    f = {
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height
                    }
                    code.append(f'{" "*pad}Pages({join_fields(f)})')
                    code.append(f'{" "*pad}{{')
                    pad += tabwidth

                elif t == b'p':
                    # Pages end
                    pad -= tabwidth
                    code.append(f'{" "*pad}}}')

                elif t == b'T':
                    # Page
                    caption = self.stream.read_str(b'\r')
                    f = {
                        'caption': f'"{caption}"'
                    }
                    code.append(f'{" "*pad}Page({join_fields(f)})')
                    code.append(f'{" "*pad}{{')
                    pad += tabwidth

                elif t == b't':
                    # Page end
                    pad -= tabwidth
                    code.append(f'{" "*pad}}}')

                else:
                    print(f'Unknown window element {t} @{self.stream.pos:04x}')

            code.append('}')

        elif c == b'w':
            print('is no window')
        else:
            raise SyntaxError('Window section not exists')
        code.append('')
        self.b_window_start = start
        self.b_window_end = self.stream.pos
        self.b_windows_listing = code

    def decompile_script(self):
        start = self.stream.pos
        code = []
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'Tab')
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'Buf1Size')
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'Buf2Size')
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'Flags')
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'SelBegin')
        lbl = self.stream.read_word_be()
        self.host_listing.set_label(lbl, f'SelEnd')
        lbl += 4
        self.host_listing.set_label(lbl, f'Res1')
        lbl += 4
        self.host_listing.set_label(lbl, f'Res2')
        lbl = self.stream.read_word_be()
        if lbl != 0xFFFF:
            if lbl & 0x8000:
                lbl &= 0x7FFF
                self.host_listing.set_label(lbl, f'OnCreate_{lbl:04X}')
                self.host_listing.set_flag_proc(lbl)
            else:
                print(f'todo1: {lbl:04X}')

        lbl = self.stream.read_word_be()
        if lbl != 0xFFFF:
            if lbl & 0x8000:
                lbl &= 0x7FFF
                self.host_listing.set_label(lbl, f'Idle_{lbl:04X}')
                self.host_listing.set_flag_proc(lbl)
            else:
                print(f'todo2: {lbl:04X}')

        next_block_offset = self.stream.read_word_be()
        host_bytecode_offset = self.stream.pos
        host_bytecode = self.stream.read_stream(next_block_offset - host_bytecode_offset)
        host_bytecode.mem_offset = 0
        self.b_host_script_start = start
        self.b_host_script_end = self.stream.pos
        self.host_listing.set_mem(host_bytecode)
        code.append('')
        code.append('$HOST')
        code.append('')
        code.extend(self.host_listing.disassemble(DisassemblerIPR, {
            'type': 'host',
            'device_labels': []
        }))

        # DEVICE
        # Entry points...
        start = self.stream.pos
        for i in range(32):
            p = self.stream.read_word_le()
            if p != 0xFFFF:
                label = f'prc_id{i}' if i != 31 else 'Idle'
                self.device_listing.set_label(p, label)
                self.device_listing.set_flag_proc(p)
        self.b_device_script_ep_start = start
        self.b_device_script_ep_end = self.stream.pos

        # bytecode, может быть шифрованный
        start = self.stream.pos
        # От текущей позиции до конца - 2 байта. CRC должно быть выровнено на границу 64bytes
        device_bytecode = self.stream.read_stream(self.stream.len - self.stream.pos - 2)
        device_bytecode.mem_offset = 0
        self.b_device_script_crypt_start = start
        self.b_device_script_crypt_end = self.stream.pos

        start = self.stream.pos
        crc = self.stream.read_word_be()
        self.b_device_script_crc_start = start
        self.b_device_script_crc_end = self.stream.pos

        code.append('')
        code.append('')
        code.append('$DEVICE')
        code.append('')

        decrypted_bin = Decoder.decode_ipr_bytecode(device_bytecode.bin, crc)
        if decrypted_bin is not None:
            device_bytecode.bin = decrypted_bin
            self.device_script = device_bytecode
            self.device_listing.set_mem(device_bytecode)
            code.extend(self.device_listing.disassemble(DisassemblerIPR, {
                'type': 'device',
                'labels': self.host_listing.dis.presets['device_labels'],
                'procs': []   # todo: add from command line
            }))
        else:
            code.append('// invalid crc bytecode')

        if self.stream.pos == self.stream.len:
            print(f'EOF OK')
        else:
            print(f'LEFT {self.stream.pos - self.stream.pos} bytes')

        code.append('')
        self.script_listing = code

    def decompile(self):
        self.host_listing = Listing()
        self.device_listing = Listing()
        try:
            self.decompile_menu()
            self.decompile_toolbar()
            self.decompile_editor()
            self.decompile_window()
            self.decompile_script()
        except (SyntaxError, MemoryNotDefined) as e:
            print(e)
            print('The file is corrupted')
