from listing import Line, Listing


class IPRDecomp:

    # noinspection SpellCheckingInspection
    io_host = {
        0: 'PBMAX',
        1: 'PBPOS',
        2: 'PIN_TEST_WINDOW',
        3: 'PIN_TEST_RESULT',
        4: 'TAB_COUNT',
        10: 'USB',
        11: 'USB_WAIT',
        12: 'USB16',
        13: 'USB16_WAIT',
        14: 'USB32',
        15: 'USB32_WAIT',
        33: 'WINDOW',
        34: 'FAST_TIMER',
        65: 'ESIZE1',
        66: 'ESIZE2',
        67: 'ESIZE3',
        68: 'FILEEXISTS',
        69: 'SW_VERSION',
        70: 'DEVICE_SERIAL',
        71: 'OPEN_FILE_DIALOG',
        72: 'SAVE_FILE_DIALOG',
        254: 'WRITE_ENABLE',
    }

    # noinspection SpellCheckingInspection
    io_device = {
        0: 'PORTA',
        1: 'PORTB',
        2: 'PORTC',
        3: 'PORTD',
        4: 'PORTE',
        5: 'TIMER',
        6: 'UART_DATA',
        7: ('VM_ID', 'UART_CR'),  # in / out
        8: 'UART_MR',
        9: 'UART_BRGR',
        10: 'USB',
        11: 'USB_WAIT',
        12: 'USB16',
        13: 'USB16_WAIT',
        14: 'USB32',
        15: 'USB32_WAIT',
        16: 'POWER',
        17: 'SPI_CR',
        18: 'SPI_DATA32',
        19: 'SPI_DATA8',
        20: 'ADC_CR',
        21: 'ADC_SR',
        22: 'ADC_DATA0',
        23: 'ADC_DATA1',
        24: ('ADC_DATA2', 'I2C_PINS'),  # in / out
        25: 'ADC_DATA3',
        26: 'IDLE_ENABLE',
        27: 'TIMER2',
        28: 'PWM0',
        29: 'PWM1',
        30: 'PWM2',
        31: 'IRQ_FLAG',
        32: 'IRQ_ENABLE',
        # 33: '???',
        34: 'FAST_TIMER',
        35: 'CAPT_VALUE',
        36: 'CAPT_CLOCK',
        37: ('CAPT_VALUE2', 'TIMER_ENABLE'),
        38: 'SPI_DATA16',
        39: 'SPI_DATA24',
        40: ('RANDOM', 'CAPT_MODE'),
        41: 'CAPT_TIMER',
        42: 'FAST_TIMER_CLOCK',

        50: 'CAPT_INTERVAL0',
        51: 'CAPT_INTERVAL1',
        52: 'CAPT_INTERVAL2',
        53: 'CAPT_INTERVAL3',
        54: 'CAPT_INTERVAL4',
        55: 'CAPT_INTERVAL5',
        56: 'CAPT_INTERVAL6',
        57: 'CAPT_INTERVAL7',
        58: 'CAPT_INTERVAL8',
        59: 'CAPT_INTERVAL9',
        60: 'BDM_ENABLE',
        61: 'BDM_TIMES',
        62: 'BDM_DATA_8',
        63: 'BDM_DATA_16',
        64: 'BDM_DATA_32',
        65: 'I2C_DATA',
        66: 'ESPI_CONFIG',
        67: 'ESPI_DATA8',
        68: 'ESPI_DATA16',
        69: 'ESPI_DATA32',
        70: 'I2C_DATA_ACK',
        71: 'I2C_ACK',
        72: ('DDEVICE_SERIAL', 'PWM0_RUN'),
        73: 'PWM0_PULSE',
        74: 'PULSE_35080',
        75: 'PORTA_PULSE',
        76: 'PWM_PULSE',
        77: 'SOUND',

        253: 'USB_INT',
        254: 'WRITE_ENABLE',    # ???
        255: 'SERIAL',

        # 21: 'BDM_SYNC_PULSE',
        # 22: 'BDM_CLOCK',
        # 23: 'BDM_MULT',
        # 28: 'SPI_CSR',
        # 29: 'DBG1',
        # 30: 'DBG2',
        # 54: 'PULSE2_35080',
        # 64: 'BDM_SYNC',
        # 71: 'ER35080',
        # 77: 'PWM_DIRECT',
    }

    patterns = []

    @classmethod
    def reg_pattern(cls, func):
        cls.patterns.append(func)

    def __init__(self, listing: Listing):
        self.listing = listing
        self.listing.dis.presets['global'] = {'emem': [], 'string': []}
        self.line_first = None
        self.pad = 0
        self.tmp_str = None
        self.last_r15 = []

    def get_ui(self, ui_id):
        ui = self.listing.dis.presets.get('ui')
        control = ui and ui.get(ui_id)
        return control or f'unknown_{ui_id}'

    def tmp_str_clear(self):
        self.tmp_str = None

    def tmp_str_append(self, s):
        self.tmp_str = s if self.tmp_str is None else f'{self.tmp_str} + {s}'

    def tmp_str_get(self):
        return "" if self.tmp_str is None else self.tmp_str

    def add_global_str(self, str_idx):
        if str_idx not in self.listing.dis.presets['global']['string']:
            self.listing.dis.presets['global']['string'].append(str_idx)

    def set_comment(self, line: Line, comment):
        padding = ' ' * self.pad * 4
        line.set_comment(padding + comment)

    def get_io_name(self, io_id, output):
        io_names = self.io_host if self.listing.dis.is_host() else self.io_device
        if io_id in io_names:
            io = io_names[io_id]
            return io if isinstance(io, str) else io[output]
        else:
            return f'IO_{io_id}'

    def set_device_label(self, ea, name, comment=None):
        if 'device_labels' in self.listing.dis.presets:
            self.listing.dis.presets['device_labels'].append((ea, name, comment))

    def get_emem_label(self, emem_id):
        emem_var = {0: 'buf0', 1: 'buf1', 2: 'sel0', 3: 'sel1', 4: 'data'}.get(emem_id, f'emem{emem_id}')
        emem = (emem_var, emem_id)
        if emem not in self.listing.dis.presets['global']['emem']:
            self.listing.dis.presets['global']['emem'].append(emem)
        return emem_var

    @staticmethod
    def is_reg_preserved(lines, reg, before_line):
        check_list = []
        if lines and before_line:
            line = lines[-1].next()
            while line < before_line:
                check_list.append(line)
                line = line.next()

            for line in check_list:
                if line.instruction in ('JMP', 'CALL', 'RET', 'SYS', 'DCALL') or \
                   line.instruction[:3] == "CMP" or \
                   line.instruction[:1] == "J" or \
                   line.instruction[:3] == "CPI" or \
                   (len(line.args) > 1 and line.arg_str(0) == reg):
                    return False

        return True

    def decompile(self, ea: int):

        if '?' in self.listing.flags(ea):
            # skip bad functions
            return

        self.line_first = self.listing.line(ea)
        self.pad = 0
        self.tmp_str_clear()
        self.last_r15 = []

        line = self.line_first
        while True:

            if 'P' in line.flags and line != self.line_first:   # конец ф-ии
                break

            next_line = None
            for p in self.patterns:
                next_line = p(self, line)
                if next_line:
                    line = next_line
                    break

            if next_line is None:
                # next line
                line = line.next()

    def post(self):
        # emem
        emem = self.listing.dis.presets['global']['emem']
        if emem:
            emem_vars = ', '.join(f'{e}={i}' for e, i in emem)
            self.listing.glob.append(f'emem {emem_vars};')
            self.listing.glob.append('')

        # string
        s = self.listing.dis.presets['global']['string']
        if s:
            str_vars = ', '.join(f'str{i}' for i in range(max(s) + 1))
            self.listing.glob.append(f'string {str_vars};')
            self.listing.glob.append('')


pat = IPRDecomp.reg_pattern


@pat
def _proc(d: IPRDecomp, line: Line):
    """
    begin proc
    """
    if line.instruction == 'PUSHR':
        line2 = line.next()
        if line2.instruction == 'ENTER':
            v = ', '.join([f'R{a}' for a in range(line2.arg(0))])
            d.set_comment(line, f'proc {line.name}({v}) {{')
            # Typically the last one or two registers are used as an unnamed variable.
            v = ', '.join([f'R{a + line2.arg(0)}' for a in range(line2.arg(1) - line2.arg(0) - 1)])
            if v:
                d.set_comment(line2, f'var {v};\n')
            else:
                d.set_comment(line2, f'\n')
            return line2.next()


@pat
def _for1(d: IPRDecomp, line: Line):
    """
    for((const)_init_;(const)_cond_;_incr_) {} instruction
    """
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_type(0) == 'r':
        line2 = line.next()
        if line2.instruction in ('LDB', 'LDW', 'LDD') and line2.arg_type(0) == 'r':
            line3 = line2.next()
            if line3.instruction[:4] == 'CMPJ' and line3.arg(0) == line.arg(0) and line3.arg(1) == line2.arg(0):
                ncond = {'E': '!=', 'NE': '=', 'GE': '<', 'LE': '>', 'L': '>=', 'G': '<='}.get(
                    line3.instruction[4:], '??')

                if line2.name:
                    d.set_comment(line3, f'for ({line.arg_str(0)} = {line.arg_str(1)}; '
                                         f'{line.arg_str(0)} {ncond} {line2.arg_str(1)}; _incr_) {{')
                    d.set_comment(line, '_init_')
                    d.set_comment(line2, '_cond_')
                else:
                    d.set_comment(line3, f'if ({line3.arg_str(0)} {ncond} {line3.arg_str(1)}) {{')
                    return line3.next()

                linee = line3.next()
                lineincr = None
                while 'P' not in linee.flags:
                    if linee.instruction == 'JMP' and linee.arg(0) == line2.ea and linee.next().ea == line3.arg(2):
                        if lineincr is not None:
                            d.set_comment(lineincr, '_incr_')
                        d.set_comment(linee, '}  // for')
                        break

                    elif linee.instruction == 'JMP' and linee.arg(0) == line2.ea:
                        d.set_comment(linee, '  continue;')

                    elif linee.instruction == 'JMP' and linee.arg(0) == line3.arg(2):
                        d.set_comment(linee, '  break;')

                    lineincr = linee
                    linee = linee.next()

                return line3.next()


@pat
def _for2(d: IPRDecomp, line: Line):
    """
    for((const)_init_;(var)_cond_;_incr_) {} instruction
    """
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_type(0) == 'r':
        line2 = line.next()
        if line2.instruction[:4] == 'CMPJ' and line2.arg(0) == line.arg(0):
            ncond = {'E': '!=', 'NE': '=', 'GE': '<', 'LE': '>', 'L': '>=', 'G': '<='}.get(line2.instruction[4:], '??')

            if line2.name:
                d.set_comment(line2, f'for ({line.arg_str(0)} = {line.arg_str(1)}; '
                                     f'{line2.arg_str(0)} {ncond} {line2.arg_str(1)}; _incr_) {{')
                d.set_comment(line, '_init_')
            else:
                d.set_comment(line2, f'if ({line2.arg_str(0)} {ncond} {line2.arg_str(1)}) {{')
                return line2.next()

            linee = line2.next()
            lineincr = None
            while 'P' not in linee.flags:
                if linee.instruction == 'JMP' and linee.arg(0) == line2.ea and linee.next().ea == line2.arg(2):
                    if lineincr is not None:
                        d.set_comment(lineincr, '_incr_')
                    d.set_comment(linee, '}  // for')
                    break

                elif linee.instruction == 'JMP' and linee.arg(0) == line2.ea:
                    d.set_comment(linee, '  continue;')

                elif linee.instruction == 'JMP' and linee.arg(0) == line2.arg(2):
                    d.set_comment(linee, '  break;')

                lineincr = linee
                linee = linee.next()

            return line2.next()


@pat
def _while(d: IPRDecomp, line: Line):
    """
    while(_cond_) ...
    """
    if line.instruction in ('LDB', 'LDW', 'LDD'):
        line2 = line.next()
        if line2.instruction[:4] == 'CMPJ' and line2.arg(1) == line.arg(0):
            ncond = {'E': '!=', 'NE': '=', 'GE': '<', 'LE': '>', 'L': '>=', 'G': '<='}.get(line2.instruction[4:], '??')

            linee = d.listing.line(line2.arg(2)-3)  # JMP xxxx = 3bytes
            if linee.instruction == 'JMP' and linee.arg(0) == line.ea:
                d.set_comment(line, '')
                d.set_comment(line2, f'while ({line2.arg_str(0)} {ncond} {line.arg_str(1)}) {{')
                d.set_comment(linee, '}  // while')

                line_ = line2.next()
                while line_ < linee:
                    if line_.instruction == 'JMP':
                        if line_.arg(0) == line.ea:
                            d.set_comment(line_, '  continue;')
                        elif line_.arg(0) == line2.arg(2):
                            d.set_comment(line_, '  break;')
                    line_ = line_.next()

                return line2.next()


@pat
def _if(d: IPRDecomp, line: Line):
    """
    if
    """
    if line.instruction[:4] == 'CMPJ':
        ncond = {'E': '!=', 'NE': '=', 'GE': '<', 'LE': '>', 'L': '>=', 'G': '<='}.get(line.instruction[4:], '??')
        d.set_comment(line, f'if ({line.arg_str(0)} {ncond} {line.arg_str(1)}) {{')
        return line.next()

    if line.instruction[:4] == 'CPIJ':
        ncond = {'E': '!=', 'NE': '='}.get(line.instruction[4:], '??')
        d.set_comment(line, f'if ({line.arg_str(0)} {ncond} {line.arg_str(1)}) {{')
        return line.next()

    if line.instruction == 'JZ':
        d.set_comment(line, f'if ({line.arg_str(0)}) {{')
        return line.next()

    if line.instruction == 'JNZ':
        d.set_comment(line, f'if ({line.arg_str(0)} = 0) {{')
        return line.next()

    if line.instruction == 'JBRC':
        d.set_comment(line, f'if ({line.arg_str(0)} & 0x{1 << line.arg(1):02x}) {{')
        return line.next()

    if line.instruction == 'JBRS':
        d.set_comment(line, f'if (({line.arg_str(0)} & 0x{1 << line.arg(1):02x}) = 0) {{')
        return line.next()


@pat
def _in(d: IPRDecomp, line: Line):
    """
    var = IO
    """
    if line.instruction == 'IN':
        r = line.arg_str(0)
        a = line.arg(1)
        io = d.get_io_name(a, False)
        d.set_comment(line, f'{r} = {io};')
        return line.next()


@pat
def _out(d: IPRDecomp, line: Line):
    """
    IO = var|cons
    """
    if line.instruction == 'OUT':
        a = line.arg(0)
        r = line.arg_str(1)
        io = d.get_io_name(a, True)
        d.set_comment(line, f'{io} = {r};\n')
        return line.next()


@pat
def _out_or(d: IPRDecomp, line: Line):
    """
    IO |= const
    """
    if line.instruction == 'ORPI':
        a = line.arg(0)
        io = d.get_io_name(a, True)
        r = line.arg(1)
        d.set_comment(line, f'{io} |= 0x{r:x};')
        return line.next()


@pat
def _out_and_not(d: IPRDecomp, line: Line):
    """
    IO &= const ^ 255
    """
    if line.instruction == 'ANDPI':
        a = line.arg(0)
        io = d.get_io_name(a, True)
        r = line.arg(1)
        d.set_comment(line, f'{io} &= 0x{r ^ 255:x} ^ 255;')
        return line.next()


@pat
def _if_in(d: IPRDecomp, line: Line):
    """
    if (IO = 0) {
    """
    if line.instruction == 'JNZIO':
        a = line.arg(0)
        io = d.get_io_name(a, False)
        d.set_comment(line, f'if ({io} = 0) {{\n')
        return line.next()

    # if line.instruction == 'JZIO':
    #     a = line.arg(0)
    #     io = d.get_io_name(a, False)
    #     d.set_comment(line, f'if ({io}) {{\n')
    #     return line.next()


@pat
def _sys_0(d: IPRDecomp, line: Line):
    """
    SYS 0 -> clear temp string
    """
    if line.instruction == 'SYS' and line.arg(0) == 0:
        d.set_comment(line, '// TMP = ""')
        d.tmp_str_clear()
        return line.next()


@pat
def _sys_2(d: IPRDecomp, line: Line):
    """
    SYS 2 -> global str = temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 2:
            d.set_comment(line, '')
            s = d.tmp_str_get()
            d.set_comment(line2, f'str{line.arg(1)} = {s};  // str{line.arg(1)} = TMP\n')
            d.add_global_str(line.arg(1))
            return line.next()


@pat
def _sys_13_host(d: IPRDecomp, line: Line):
    """
    $HOST
    SYS 13 -> put global str to temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 13:
            s = f'str{line.arg(1)}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            d.add_global_str(line.arg(1))
            return line.next()


@pat
def _sys_13_device(d: IPRDecomp, line: Line):
    """
    $DEVICE
    SYS 13 -> STREAMPIN = PORT[ABD].bit
    """
    if line.instruction == 'LDW' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 13:
            port = 'PORT' + chr(ord('A') + (line.arg(1) >> 8))
            bit_number = len(bin(line.arg(1) & 0xFF)) - 3
            d.set_comment(line, '')
            d.set_comment(line2, f'STREAMPIN = {port}.{bit_number};')
            return line2.next()


@pat
def _sys_3(d: IPRDecomp, line: Line):
    """
    SYS 3 -> put int into temp string
    """
    # local int
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 3:
            v = line.arg_str(1)
            s = f'#i.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # const int
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 3:
            v = line.arg(1)
            s = f'#i.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # global int
    if line.instruction in ('LDMB', 'LDMW', 'LDMD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 3:
            v = line.arg_str(1)
            s = f'#i.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()


@pat
def _sys_4(d: IPRDecomp, line: Line):
    """
    SYS 4 -> put char into temp string
    """
    # local char
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 4:
            v = line.arg_str(1)
            s = f'#c.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # const char
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 4:
            v = line.arg(1)
            s = f'#c.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # global char
    if line.instruction in ('LDMB', 'LDMW', 'LDMD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 4:
            v = line.arg_str(1)
            s = f'#c.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()


@pat
def _sys_5_6_7_8(d: IPRDecomp, line: Line):
    """
    SYS [5,6,7,8] - > put hex into temp string
    """
    # local hex
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) in (5, 6, 7, 8):
            w = line2.arg(0) - 4
            v = line.arg_str(1)
            s = f'#h{w}.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # const hex
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) in (5, 6, 7, 8):
            w = line2.arg(0) - 4
            v = line.arg(1)
            s = f'#h{w}.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, f'// {v} == 0x{v:02x}')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()

    # global hex
    if line.instruction in ('LDMB', 'LDMW', 'LDMD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) in (5, 6, 7, 8):
            w = line2.arg(0) - 4
            v = line.arg_str(1)
            s = f'#h{w}.{v}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()


@pat
def _sys_1(d: IPRDecomp, line: Line):
    """
    SYS 1 -> put string into temp string
    """
    if line.instruction == 'LDW' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 1:
            str_offset = line.arg(1)
            d.listing.set_string0(str_offset)
            line.set_arg_type(1, 'o')
            s = d.listing.line(str_offset).arg(0)
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()


@pat
def _sys_43(d: IPRDecomp, line: Line):
    """
    SYS 43 -> put FILENAME into temp string
    """
    if line.instruction == 'SYS' and line.arg(0) == 43:
        s = 'FILENAME'
        d.tmp_str_append(s)
        d.set_comment(line, f'// TMP += {s}')
        return line.next()


@pat
def _sys_9(d: IPRDecomp, line: Line):
    """
    SYS 9 -> mbox(temp string, NUM)
    """
    if line.instruction == 'ORD' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 9:
            a = line.arg(1)
            # lo = a & 0xFFFF
            hi = a >> 16
            s = d.tmp_str_get()
            d.set_comment(line, f'// ({hi} << 16)')
            d.set_comment(line2, f'R15 = mbox({s}, {hi});  // R15 = mbox(TMP, {hi})\n')
            return line2.next()


@pat
def _sys_12(d: IPRDecomp, line: Line):
    """
    SYS 12 -> print(temp string)
    """
    if line.instruction == 'SYS' and line.arg(0) == 12:
        s = d.tmp_str_get()
        d.set_comment(line, f'print({s});  // print(TMP)\n')
        return line.next()


@pat
def _sys_26(d: IPRDecomp, line: Line):
    """
    SYS 26 -> backup(temp string)
    """
    if line.instruction == 'SYS' and line.arg(0) == 26:
        s = d.tmp_str_get()
        d.set_comment(line, f'backup({s});  // backup(TMP)\n')
        return line.next()


@pat
def _sys_28(d: IPRDecomp, line: Line):
    """
    SYS 28 -> picture_idR15 = temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 28:
            s = d.tmp_str_get()
            c = d.get_ui(line.arg(1))
            d.set_comment(line, '')
            d.set_comment(line2, f'{c} = {s};  // {c} = TMP\n')
            return line2.next()


@pat
def _sys_15_host(d: IPRDecomp, line: Line):
    """
    SYS 15 -> control_R15 = temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 15:
            s = d.tmp_str_get()
            c = d.get_ui(line.arg(1))
            d.set_comment(line, '')
            d.set_comment(line2, f'{c} = {s};  // {c} = TMP\n')
            return line2.next()


@pat
def _sys_15_device(d: IPRDecomp, line: Line):
    """
    SYS 15 -> StreamOut(R15, R14h, R14l)
    """
    # R15
    # 1:    LDx|MOV|LDMD    R15, Rx or const or gvar
    #
    # R14h
    # 2:    MOV|LDMx        R14, Rx or gvar
    # 22:   RL              R14, 16
    #   or
    # 2:    LDD             R14, const<<16
    #
    # R14l
    # 3:    OR|ORx|ORMx     R14 or const
    #
    # flags (optional)
    # 32:   ORD             R14, 0x40000000
    #
    # 4:    SYS             15
    if line.instruction in ('MOV', 'LDB', 'LDW', 'LDD', 'LDMD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction in ('MOV', 'LDMB', 'LDMW', 'LDMD', 'LDD') and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line2.instruction != 'LDD' and \
                    line3.instruction == 'RL' and line3.arg_str(0) == 'R14' and line3.arg(1) == 16:
                line22 = line3
                line3 = line22.next()
            else:
                line22 = None
            if line3.instruction in ('OR', 'ORB', 'ORW', 'ORD', 'ORMB', 'ORMW', 'ORMD') and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'ORD' and line4.arg_str(0) == 'R14' and line4.arg(1) == 0x40000000:
                    line32 = line4
                    line4 = line32.next()
                else:
                    line32 = None
                if line4.instruction == 'SYS' and line4.arg(0) == 15:

                    if line32:
                        d.set_comment(line32, '// R15 is byte array')
                        if line.instruction != 'MOV':
                            a0 = line.arg(1)
                            label = f'b_{a0:04X}'  # byte array
                            d.listing.set_label(a0, label, False)
                            line.set_arg_type(1, 'o')
                    a0 = line.arg_str(1)

                    if line22:
                        a1 = line2.arg_str(1)
                        d.set_comment(line2, '')
                        d.set_comment(line22, '')
                    else:
                        a1 = line2.arg(1) >> 16
                        d.set_comment(line2, f'// {a1} << 16')

                    a2 = line3.arg_str(1)

                    d.set_comment(line, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'StreamOut({a0}, {a1}, {a2});\n')

                    return line4.next()


@pat
def _sys_16(d: IPRDecomp, line: Line):
    """
    SYS 16 -> (byte|word|dword)device.R14 = R15
    """
    if line.instruction in ('MOV', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LDW' and line2.arg_str(0) == 'R14' and line2.arg_type(1) == 'd':
            line3 = line2.next()
            if line3.instruction == 'ORD' and line3.arg_str(0) == 'R14' and line3.arg_type(1) == 'd':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 16:
                    w = line3.arg(1) >> 16
                    w, pref = {1: ('byte', 'b_'), 2: ('word', 'w_'), 4: ('dword', 'd_')}.get(w, str(w))
                    dev_label = f'{pref}{line2.arg(1):04X}'
                    d.set_device_label(line2.arg(1), dev_label)
                    d.set_comment(line, f'')
                    d.set_comment(line2, '')
                    d.set_comment(line3, f'// {line3.arg(1)}:{line2.arg(1)} is {w}:device.{dev_label}')
                    d.set_comment(line4, f'({w})device.{dev_label} = {line.arg_str(1)};\n')
                    return line4.next()

    # device.any_array[NUM] = any
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LDD' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'RL' and line3.arg_str(0) == 'R14':
                w = line3.arg(1)
                line4 = line3.next()
            else:
                w = 0
                line4 = line3
                line3 = None
            if line4.instruction == 'ADDW' and line4.arg_str(0) == 'R14':
                line5 = line4.next()
                if line5.instruction == 'SYS' and line5.arg(0) == 16:
                    w, pref = {0: ('byte', 'b_'), 1: ('word', 'w_'), 2: ('dword', 'd_')}.get(w, str(w))
                    dev_label = f'{pref}{line4.arg(1):04X}'
                    d.set_device_label(line4.arg(1), dev_label)
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    if line3:
                        d.set_comment(line3, '')
                    d.set_comment(line4, '')
                    d.set_comment(line5, f'({w})device.{dev_label}[{line2.arg_str(1)}] = {line.arg_str(1)};\n')
                    return line5.next()

    # device.byte_array[local_var] = any
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LMA' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 16:
                w = 'byte'
                dev_label = f'b_{line2.arg(2):04X}'
                d.set_device_label(line2.arg(2), dev_label)
                d.set_comment(line, '')
                d.set_comment(line2, '')
                d.set_comment(line3, f'({w})device.{dev_label}[{line2.arg_str(1)}] = {line.arg_str(1)};\n')
                return line3.next()

    # device.byte_array[expression] = any
    if line.instruction == 'LMA' and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 16:
            w = 'byte'
            dev_label = f'b_{line.arg(2):04X}'
            d.set_device_label(line.arg(2), dev_label)
            d.set_comment(line, '')
            d.set_comment(line2, f'({w})device.{dev_label}[{line.arg_str(1)}] = R15;\n')
            return line2.next()

    # device.word_array|dword_array[local_var] = any
    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'MOV' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'RL' and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'ADDW' and line4.arg_str(0) == 'R14':
                    line5 = line4.next()
                    if line5.instruction == 'SYS' and line5.arg(0) == 16:
                        w = line3.arg(1)
                        w, pref = {0: ('byte', 'b_'), 1: ('word', 'w_'), 2: ('dword', 'd_')}.get(w, str(w))
                        dev_label = f'{pref}{line4.arg(1):04X}'
                        d.set_device_label(line4.arg(1), dev_label)
                        d.set_comment(line, '')
                        d.set_comment(line2, '')
                        d.set_comment(line3, '')
                        d.set_comment(line4, '')
                        d.set_comment(line5, f'({w})device.{dev_label}[{line2.arg_str(1)}] = {line.arg_str(1)};\n')
                        return line5.next()

    # device.word_array|dword_array[expression] = any
    if line.instruction == 'MOV' and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction == 'RL' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'ADDW' and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 16:
                    w = line2.arg(1)
                    w, pref = {1: ('word', 'w_'), 2: ('dword', 'd_')}.get(w, str(w))
                    dev_label = f'{pref}{line3.arg(1):04X}'
                    d.set_device_label(line3.arg(1), dev_label)
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'({w})device.{dev_label}[{line.arg_str(1)}] = R15;\n')
                    return line4.next()


@pat
def _sys_17(d: IPRDecomp, line: Line):
    """
    SYS 17 -> R15 = device.prc_id_R15low_byte(R15hi_byte args)
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 17:
            proc_id = line.arg(1)
            line3 = line2.next()
            if line3.instruction == 'MOV' and line3.arg_str(1) == 'R15':
                d.set_comment(line, '')
                d.set_comment(line2, '')
                d.set_comment(line3, f'{line3.arg_str(0)} = device.prc_id{proc_id}();\n')
                return line3.next()
            else:
                d.set_comment(line, '')
                d.set_comment(line2, f'R15 = device.prc_id{proc_id}();\n')
                return line2.next()

    if line.instruction == 'LDB' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'ORW' and line2.arg_str(0) == 'R15' and line2.arg_type(1) == 'd':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 17:
                a = line2.arg(1)
                proc_id = line.arg(1)
                n = a >> 8
                line4 = line3.next()
                if line4.instruction == 'MOV' and line4.arg_str(1) == 'R15':
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'{line4.arg_str(0)} = device.prc_id{proc_id}(<{n} args>);\n')
                    return line3.next()
                else:
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, f'R15 = device.prc_id{proc_id}(<{n} args>);\n')
                    return line3.next()


@pat
def _sys_18(d: IPRDecomp, line: Line):
    """
    SYS 18 -> device.prc_id_R15low_byte(R15hi_byte args)
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 18:
            d.set_comment(line, '')
            d.set_comment(line2, f'device.prc_id{line.arg(1)}();\n')
            return line2.next()

    if line.instruction == 'LDB' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'ORW' and line2.arg_str(0) == 'R15' and line2.arg_type(1) == 'd':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 18:
                a = line2.arg(1)
                proc_id = line.arg(1)
                n = a >> 8
                d.set_comment(line, f'id {proc_id}')
                d.set_comment(line2, f'args {n}')
                d.set_comment(line3, f'device.prc_id{proc_id}(<{n} args>);\n')
                return line3.next()


@pat
def _sys_19(d: IPRDecomp, line: Line):
    """
    SYS 19 -> R15 = (byte|word|dword)device.R15l
    """
    if line.instruction == 'LDD' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 19:
            # SYS 19. R15hi - len bytes(1,2 or 4), R15lo = offset to device variable
            a = line.arg(1)
            w = a >> 16
            w, pref = {1: ('byte', 'b_'), 2: ('word', 'w_'), 4: ('dword', 'd_')}.get(w, str(w))
            o = a & 0xFFFF
            dev_label = f'{pref}{o:04X}'
            d.set_device_label(o, dev_label)
            d.set_comment(line, f'/* {a} is {w}:device.{dev_label} */')
            d.set_comment(line2, f'R15 = ({w})device.{dev_label};')
            return line2.next()

    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'ADDD' and line2.arg_str(0) == 'R15' and line2.arg_type(1) == 'd':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 19:
                # SYS 19. R15hi - len bytes(1,2 or 4), R15lo = offset to device variable
                a = line2.arg(1)
                w = a >> 16
                w, pref = {1: ('byte', 'b_'), 2: ('word', 'w_'), 4: ('dword', 'd_')}.get(w, str(w))
                o = a & 0xFFFF
                dev_label = f'{pref}{o:04X}'
                d.set_device_label(o, dev_label)
                d.set_comment(line, '')
                d.set_comment(line2, f'/* {a} is {w}:device.{dev_label} */')
                d.set_comment(line3, f'R15 = ({w})device.{dev_label}[{line.arg_str(1)}];')
                return line3.next()

    if line.instruction == 'MOV' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'RL' and line2.arg_str(0) == 'R15' and line2.arg_type(1) == 'd':
            line3 = line2.next()
            if line3.instruction == 'ADDD' and line3.arg_str(0) == 'R15':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 19:
                    a = line3.arg(1)
                    w = a >> 16
                    w, pref = {1: ('byte', 'b_'), 2: ('word', 'w_'), 4: ('dword', 'd_')}.get(w, str(w))
                    o = a & 0xFFFF
                    i = line.arg_str(1)
                    dev_label = f'{pref}{o:04X}'
                    d.set_device_label(o, dev_label)
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, f'/* {a} is {w}:device.{dev_label} /*')
                    d.set_comment(line4, f'R15 = ({w})device.{dev_label}[{i}];')
                    return line4.next()


@pat
def _sys_20(d: IPRDecomp, line: Line):
    """
    SYS 20 -> block|memcopy(R15 = device.R14l, R14h)
    """
    if line.instruction == 'LDW' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LDW' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'ORD' and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 20:
                    a1 = line.arg(1)
                    host_label = f'b_{a1:04X}'
                    line.set_arg_type(1, 'o')
                    dev_label = f'b_{line2.arg(1):04X}'
                    a3 = line3.arg(1) >> 16
                    d.listing.set_label(a1, host_label)
                    d.listing.set_comment(a1, f'{host_label}[{a3}]')
                    d.set_device_label(line2.arg(1), dev_label, f'{dev_label}[{a3}]')
                    d.set_comment(line, f'/* {host_label} is byte array */')
                    d.set_comment(line2, f'/* device.{dev_label} */')
                    d.set_comment(line3, f'/* ({a3} << 16) */')
                    d.set_comment(line4, f'memcopy({host_label} = device.{dev_label}, {a3});\n')
                    return line4.next()

    if line.instruction == 'LDW' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LDW' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'RL':
                line4 = line3.next()
                if line4.instruction == 'OR' and line4.arg_str(0) == 'R14' and line4.arg_str(1) == line3.arg_str(0):
                    line5 = line4.next()
                    if line5.instruction == 'SYS' and line5.arg(0) == 20:
                        a1 = line.arg(1)
                        host_label = f'b_{a1:04X}'
                        line.set_arg_type(1, 'o')
                        dev_label = f'b_{line2.arg(1):04X}'
                        # a3 = line4.arg(1) >> 16
                        a3 = line3.arg_str(0)
                        d.listing.set_label(a1, host_label, False)
                        d.listing.set_comment(a1, f'{host_label}[]')
                        d.set_device_label(line2.arg(1), dev_label, f'{dev_label}[]')
                        d.set_comment(line, f'{a3} is arg2')
                        d.set_comment(line2, '')
                        d.set_comment(line3, '')
                        d.set_comment(line4, '')
                        d.set_comment(line5, f'memcopy({host_label} = device.{dev_label}, arg2);\n')
                        return line5.next()


@pat
def _sys_21(d: IPRDecomp, line: Line):
    """
    SYS 21 -> block|memcopy(buf_R15h[R15l] = device.R14l, R14h)
    """
    # R15 | 0x00000000 - buf0
    # R15 | 0x40000000 - buf1 and any other
    # R15 | 0x20000000 - data
    #
    #
    # R15
    # 1:    LDD     R15, flags for emem_id | index
    #   or
    # 1:    MOV     R15, Rx
    # 12:   ORD     R15, flags for emem_id      optional
    #
    # R14
    # ?:    R14 = <expression>                  optional
    #   or
    # 2:    LDW     R14, device.offset
    #
    # 3:    RL      Rx, 16
    # 32:   OR      R14, Rx
    #   or
    # 3:    ORD     R14, len<<16
    #
    # 4:    SYS     21
    line1 = line
    line2 = line1.next()
    if line1.instruction == 'MOV' and line1.arg_str(0) == 'R15':
        if line2.instruction == 'ORD' and line2.arg_str(0) == 'R15':
            line12 = line2
            line2 = line12.next()
            d.last_r15 = [line1, line12]
        else:
            d.last_r15 = [line1]
    elif line1.instruction == 'LDD' and line1.arg_str(0) == 'R15':
        d.last_r15 = [line1]
    else:
        line2 = line1

    if line2 and line2.instruction == 'LDW' and line2.arg_str(0) == 'R14':
        line3 = line2.next()
        line4 = line3.next()
        line32 = None
        if line3.instruction == 'RL' and line3.arg(1) == 16 and \
                line4.instruction == 'OR' and line3.arg_str(0) == line4.arg_str(1):
            line32 = line4
            line4 = line32.next()
        elif line3.instruction == 'ORD' and line3.arg_str(0) == 'R14':
            pass
        else:
            line4 = None

        if line4 and line4.instruction == 'SYS' and line4.arg(0) == 21:
            if not d.is_reg_preserved(d.last_r15, 'R15', line2):
                d.last_r15 = []
            line1 = d.last_r15.pop(0) if d.last_r15 else None
            line12 = d.last_r15.pop(0) if d.last_r15 else None

            if line12:
                flags = line12.arg(1)
                d.set_comment(line12, '// emem buf')
                idx = f'emem index: {line1.arg_str(1)}'
                d.set_comment(line1, f'// {idx}')
            else:
                if line1:
                    tmp = line1.arg(1)
                    flags = tmp & 0xFF000000
                    idx = tmp & 0xFFFFFF
                    d.set_comment(line1, f'// emem index: {idx}')
                else:
                    flags = 0
                    idx = 'R15l'

            emem_id = {0: 0, 0x20000000: 4}.get(flags, 1)
            emem_label = d.get_emem_label(emem_id)
            d.set_comment(line2, '// device.array variable offset')
            dev_label = f'b_{line2.arg(1):04X}'
            d.set_device_label(line2.arg(1), dev_label, f'byte {dev_label}[];')

            if line32:
                d.set_comment(line32, '')
                a3 = line3.arg_str(0)
                d.set_comment(line3, f'length: {a3}')
            else:
                a3 = line3.arg(1) >> 16
                d.set_comment(line3, f'// length: {a3} << 16')

            d.set_comment(line4, f'memcopy({emem_label}[{idx}] = device.{dev_label}, {a3});\n')
            return line4.next()


@pat
def _sys_22(d: IPRDecomp, line: Line):
    """
    SYS 22 -> block|memcopy(device.R14l = R15, R14h)
    """
    if line.instruction == 'LDW' and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction == 'LDW' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'ORD' and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 22:
                    line2.set_arg_type(1, 'o')
                    dev_label = f'b_{line.arg(1):04X}'
                    host_label = f'b_{line2.arg(1):04X}'
                    a3 = line3.arg(1) >> 16
                    d.listing.set_label(line2.arg(1), host_label)
                    d.listing.set_comment(line2.arg(1), f'{host_label}[{a3}]')
                    d.set_device_label(line.arg(1), dev_label, f'{dev_label}[{a3}]')
                    d.set_comment(line, f'/* device.{dev_label} */')
                    d.set_comment(line2, '')
                    d.set_comment(line3, f'/* ({a3} << 16) */')
                    d.set_comment(line4, f'memcopy(device.{dev_label} = {host_label}, {a3});\n')
                    return line4.next()


@pat
def _sys_23(d: IPRDecomp, line: Line):
    """
    SYS 23 -> block|memcopy(device.R14l=buf[R15],R14h)
    """
    if line.instruction == 'LDW' and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction == 'MOV' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'RL' and line3.arg(1) == 16:
                line4 = line3.next()
                if line4.instruction == 'OR' and line4.arg_str(0) == 'R14':
                    line5 = line4.next()
                    if line5.instruction == 'SYS' and line5.arg(0) == 23:
                        dev_label = f'b_{line.arg(1):04X}'
                        d.set_device_label(line.arg(1), dev_label)
                        a3 = line4.arg_str(1)
                        d.set_comment(line, f'/* device.{dev_label} */')
                        d.set_comment(line2, '')
                        d.set_comment(line3, '')
                        d.set_comment(line4, '')
                        d.set_comment(line5, f'memcopy(device.{dev_label} = buf_?[{line2.arg_str(1)}], {a3});\n')
                        # get_emem_label(?)
                        return line5.next()

    # block|memcopy(device.R14l=buf[any],const)
    if line.instruction == 'LDW' and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction in ('MOV', 'LDD') and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'ORD' and line3.arg_str(0) == 'R14':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 23:
                    dev_label = f'b_{line.arg(1):04X}'
                    d.set_device_label(line.arg(1), dev_label)
                    a3 = line3.arg(1) >> 16
                    d.set_comment(line, f'/* device.{dev_label} */')
                    d.set_comment(line2, '')
                    d.set_comment(line3, f'/* ({a3} << 16) */')
                    d.set_comment(line4, f'memcopy(device.{dev_label} = buf_?[{line2.arg_str(1)}], {a3});\n')
                    # get_emem_label(?)
                    return line4.next()

    # block|memcopy(device.R14l=buf[any],any)
    if line.instruction == 'RL' and line.arg(1) == 16:
        line2 = line.next()
        if line2.instruction == 'OR' and line2.arg_str(0) == 'R14' and line.arg_str(0) == line2.arg_str(1):
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 23:
                dev_label = 'device.(LOWORD(R14))'
                a3 = line2.arg_str(1)
                d.set_comment(line, '')
                d.set_comment(line2, '')
                d.set_comment(line3, f'memcopy({dev_label} = buf_?[R15], {a3});\n')
                # get_emem_label(?)
                return line3.next()


@pat
def _sys_24(d: IPRDecomp, line: Line):
    """
    SYS 24 -> control_idR14.color = R15
    """
    if line.instruction in ('LDD', 'MOV') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'LDD' and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 24:
                d.set_comment(line, '')
                d.set_comment(line2, '')
                c = d.get_ui(line2.arg(1))
                v = line.arg_str(1) if line.arg_type(1) == 'r' else f'0x{line.arg(1):06x}'
                d.set_comment(line3, f'{c}.color = {v};\n')
                return line3.next()


@pat
def _sys_25(d: IPRDecomp, line: Line):
    """
    SYS 25 -> control_R14.color|fontcolor = R15
    """
    if line.instruction in ('LDW', 'LDD') and line.arg_str(0) == 'R14':
        line2 = line.next()
        if line2.instruction == 'ORD' and line2.arg_str(0) == 'R14' and line2.arg(1) == 0x80000000:
            line11 = line2
            line2 = line2.next()
        else:
            line11 = None
        if line2.instruction in ('LDD', 'MOV') and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 25:
                line.set_arg_type(1, 'o')
                d.set_comment(line, '')
                d.set_comment(line2, '')
                ui = d.listing.line(line.arg(1)).name
                v = line2.arg_str(1) if line2.arg_type(1) == 'r' else f'0x{line2.arg(1):06x}'
                attr = 'fontcolor' if line11 else 'color'
                if line11:
                    d.set_comment(line11, '')
                d.set_comment(line3, f'{ui}.{attr} = {v};\n')
                return line3.next()


@pat
def _sys_29(d: IPRDecomp, line: Line):
    """
    SYS 29 -> FILENAME = TMP
    """
    if line.instruction == 'SYS' and line.arg(0) == 29:
        s = d.tmp_str_get()
        d.set_comment(line, f'FILENAME = {s};  // FILENAME = TMP\n')
        return line.next()


@pat
def _sys_30_31(d: IPRDecomp, line: Line):
    """
    SYS 30 -> SaveToFile(...)

    SYS 31 -> LoadFromFile(...)
    """
    # emem
    if line.instruction == 'LDD' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) in (30, 31):
            v = line.arg(1)
            if v & 0x80000000 == 0x80000000:
                # emem buf
                emem_id = v ^ 0x80000000
                emem_label = d.get_emem_label(emem_id)
                d.set_comment(line, f'// {emem_id} | 0x80000000')
                d.set_comment(line2, f'{"SaveToFile" if line2.arg(0) == 30 else "LoadFromFile"}({emem_label});\n')
                return line2.next()

    # ram_buf
    if line.instruction == 'LDW' and line.arg_str(0) == 'R15' and line.arg_type(1) == 'd':
        line2 = line.next()
        if line2.instruction == 'ORD' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) in (30, 31):
                a1 = line.arg(1)
                label = f'b_{a1:04X}'
                d.listing.set_label(a1, label, False)
                line.set_arg_type(1, 'o')
                a3 = line2.arg(1) >> 16
                d.listing.set_comment(a1, f'byte {label}[{a3}];')
                d.set_comment(line, f'// {line.arg_str(1)} is a byte array, {a3} bytes length')
                d.set_comment(line2, f'// ({a3} << 16)')
                d.set_comment(line3, f'{"SaveToFile" if line3.arg(0) == 30 else "LoadFromFile"}({line.arg_str(1)});\n')
                return line3.next()


@pat
def _sys_33(d: IPRDecomp, line: Line):
    """
    SYS 33 -> text_R15 = temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 33:
            s = d.tmp_str_get()
            d.set_comment(line, '')
            d.set_comment(line2, f'text_{line.arg(1):04X} = {s};  // text_{line.arg(1):04X} = TMP\n')
            return line2.next()


@pat
def _sys_34(d: IPRDecomp, line: Line):
    """
    SYS 34 -> text_R15 = temp string
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 34:
            v = line.arg(1)
            s = f'text_{v:04X}'
            d.tmp_str_append(s)
            d.set_comment(line, '')
            d.set_comment(line2, f'// TMP += {s}')
            return line2.next()


@pat
def _sys_40(d: IPRDecomp, line: Line):
    """
    SYS 40 -> R15 = len(str<stack_arg>)
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'PUSH' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 40:
                line4 = line3.next()
                if line4.instruction == 'MOV' and line4.arg_str(1) == 'R15':
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'{line4.arg_str(0)} = len(str{line.arg(1)});\n')
                    d.add_global_str(line.arg(1))
                    return line4.next()


@pat
def _sys_42(d: IPRDecomp, line: Line):
    """
    SYS 42 -> R15 = toInt(str<stack_arg>)
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'PUSH' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 42:
                line4 = line3.next()
                if line4.instruction == 'MOV' and line4.arg_str(1) == 'R15':
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'{line4.arg_str(0)} = toInt(str{line.arg(1)});')
                    d.add_global_str(line.arg(1))
                    return line4.next()

    if line.instruction == 'PUSH':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 42:
            line3 = line2.next()
            if line3.instruction == 'MOV' and line3.arg_str(1) == 'R15':
                d.set_comment(line, '')
                d.set_comment(line2, '')
                d.set_comment(line3, f'{line3.arg_str(0)} = toInt(str{line.arg_str(0)});')
                # d.add_global_str(line.arg(1))
                return line3.next()


@pat
def _sys_41(d: IPRDecomp, line: Line):
    """
    SYS 41 -> R15 = isDigit(str<stack_arg>)
    """
    if line.instruction == 'LDB' and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'PUSH' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'SYS' and line3.arg(0) == 41:
                line4 = line3.next()
                if line4.instruction == 'MOV' and line4.arg_str(1) == 'R15':
                    d.set_comment(line, '')
                    d.set_comment(line2, '')
                    d.set_comment(line3, '')
                    d.set_comment(line4, f'{line4.arg_str(0)} = isDigit(str{line.arg(1)});')
                    d.add_global_str(line.arg(1))
                    return line4.next()


@pat
def _sys_50(d: IPRDecomp, line: Line):
    """
    SYS 50 -> R15 = str<stack_arg0>[<stack_arg1>]
    """
    if line.instruction == 'PUSH':
        line2 = line.next()
        if line2.instruction == 'LDB' and line2.arg_str(0) == 'R15':
            line3 = line2.next()
            if line3.instruction == 'PUSH' and line3.arg_str(0) == 'R15':
                line4 = line3.next()
                if line4.instruction == 'SYS' and line4.arg(0) == 50:
                    line5 = line4.next()
                    if line5.instruction == 'MOV' and line5.arg_str(1) == 'R15':
                        d.set_comment(line, '// str<idx>')
                        d.set_comment(line2, '')
                        d.set_comment(line3, '// str<id>')
                        d.set_comment(line4, '')
                        d.set_comment(line5, f'{line5.arg_str(0)} = str{line2.arg(1)}[{line.arg_str(0)}];')
                        d.add_global_str(line2.arg(1))
                        return line5.next()


@pat
def _call(d: IPRDecomp, line: Line):
    """
    proc()
    """
    if line.instruction == 'CALL':
        a = line.arg(0)
        a = d.listing.get_label(a)
        line2 = line.next()
        if line2.instruction == 'MOV' and line2.arg_str(1) == 'R15':
            d.set_comment(line, '')
            d.set_comment(line2, f'{line2.arg_str(0)} = {a}();\n')
            return line2.next()
        else:
            d.set_comment(line, f'{a}();\n')
            return line.next()


@pat
def _sys_10(d: IPRDecomp, line: Line):
    """
    SYS 10 -> ShowWindow
    """
    if line.instruction == 'SYS' and line.arg(0) == 10:
        d.set_comment(line, f'ShowWindow;\n')
        return line.next()


@pat
def _sys_11(d: IPRDecomp, line: Line):
    """
    SYS 11 -> CloseWindow
    """
    if line.instruction == 'SYS' and line.arg(0) == 11:
        d.set_comment(line, f'CloseWindow;\n')
        return line.next()


@pat
def _sys_14(d: IPRDecomp, line: Line):
    """
    SYS 14 -> Delay(R15)
    """
    if line.instruction in ('LDB', 'LDW', 'LDD', 'MOV') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'SYS' and line2.arg(0) == 14:
            a = line.arg_str(1)
            d.set_comment(line, f'')
            d.set_comment(line2, f'Delay({a});\n')
            return line2.next()


@pat
def _return(d: IPRDecomp, line: Line):
    """
    return
    """
    if line.instruction == 'POPR' and line.name:
        line2 = line.next()
        if line2.instruction == 'RET':
            label = f'end_{d.line_first.name}'
            d.listing.set_label(line.ea, label)
            line_ = d.line_first
            line_pre = None
            while True:
                if 'P' in line_.flags and line_ != d.line_first:    # конец ф-ии
                    break
                if line_.instruction == 'JMP' and line_.arg_str(0) == label:
                    if line_pre and line_pre.instruction in ('MOV', 'LDB', 'LDW', 'LDD') and \
                            line_pre.arg_str(0) == 'R15':
                        d.set_comment(line_pre, '')
                        d.set_comment(line_, f'return({line_pre.arg_str(1)});')
                    else:
                        d.set_comment(line_, 'return;')
                line_pre = line_
                line_ = line_.next()
            return line2.next()

    if line.instruction in ('MOV', 'LDB', 'LDW', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction == 'POPR':
            line3 = line2.next()
            if line3.instruction == 'RET':
                d.set_comment(line, f'return({line.arg_str(1)});')
                # do not put return


@pat
def _global_var(d: IPRDecomp, line: Line):
    """
    global vars
    """
    if line.instruction in ('STMB', 'STMW', 'STMD'):
        d.set_comment(line, f'{line.arg_str(0)} = {line.arg_str(1)};')
        return line.next()

    if line.instruction in ('LDMB', 'LDMW', 'LDMD'):
        d.set_comment(line, f'{line.arg_str(0)} = {line.arg_str(1)};')
        return line.next()


@pat
def _emem(d: IPRDecomp, line: Line):
    """
    emem buf=...
    """
    if line.instruction in ('LDB', 'LDW', 'LDD') and line.arg_str(0) == 'R15':
        line2 = line.next()
        if line2.instruction in ('LDB', 'LDW', 'LDD') and line2.arg_str(0) == 'R14':
            line3 = line2.next()
            if line3.instruction == 'STEM' and line3.arg_str(1) == 'R14' and line3.arg_str(2) == 'R15':
                d.set_comment(line, f'')
                d.set_comment(line2, f'')
                emem_id = line3.arg(0)
                idx = line2.arg(1)
                v = line.arg(1)
                emem_label = d.get_emem_label(emem_id)
                d.set_comment(line3, f'{emem_label}[{idx}] = {v};\n')
                return line3.next()

    if line.instruction == 'STEM':
        emem_id = line.arg(0)
        idx = line.arg_str(1)
        v = line.arg_str(2)
        emem_label = d.get_emem_label(emem_id)
        d.set_comment(line, f'{emem_label}[{idx}] = {v};\n')
        return line.next()

    if line.instruction == 'LDEM':
        emem_id = line.arg(0)
        v = line.arg_str(1)
        idx = line.arg_str(2)
        emem_label = d.get_emem_label(emem_id)
        d.set_comment(line, f'{v} = {emem_label}[{idx}];\n')
        return line.next()


@pat
def _array(d: IPRDecomp, line: Line):
    """
    """
    if line.instruction in ('AWRB', 'AWRW', 'AWRD'):
        v = line.arg_str(0)
        idx = line.arg_str(1)
        a = line.arg_str(2)
        d.set_comment(line, f'{v}[{idx}] = {a};\n')
        return line.next()

    if line.instruction in ('ARDB', 'ARDW', 'ARDD'):
        a = line.arg_str(0)
        v = line.arg_str(1)
        idx = line.arg_str(2)
        d.set_comment(line, f'{a} = {v}[{idx}];\n')
        return line.next()

@pat
def _(d: IPRDecomp, line: Line):
    if line.instruction == 'ADDW':
        line2 = line.next()
        if line2.instruction == 'LDIB' and line2.arg(1) == line.arg(0):
            a0 = line.arg(1)
            label = f'b_{a0:04X}'  # byte array
            d.listing.set_label(a0, label, False)
            line.set_arg_type(1, 'o')

            d.set_comment(line, '')
            d.set_comment(line2, f'{line2.arg_str(0)} = {line.arg_str(1)}[{line.arg_str(0)}]')