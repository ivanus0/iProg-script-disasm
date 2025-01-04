import struct
import des


class Decoder:
    most_popular_sn = [1, 777, 19, 35, 45, 55, 325, 2048, 49339]
    detected_sn = []
    sn_list = None
    ignore_check = False
    bruteforce = False
    brute_quick = False
    brute_all = False

    @classmethod
    def init_args(cls, args):
        cls.bruteforce = args.bruteforce
        if cls.bruteforce:
            cls.sn_list = [range(65536)]
        else:
            cls.sn_list = args.sn

        if cls.sn_list is None:
            cls.sn_list = cls.most_popular_sn

        cls.ignore_check = args.ignore_check
        cls.brute_quick = args.brute_quick
        cls.brute_all = args.brute_all

    @classmethod
    def serial_numbers(cls):
        if cls.sn_list:
            for snl in cls.sn_list:
                if isinstance(snl, int):
                    yield snl
                else:
                    for sn in snl:
                        yield sn

            if cls.brute_all:
                # do unpack
                cls.brute_all = False
                for sn in cls.detected_sn:
                    yield sn

    @classmethod
    def decode_ipr_bytecode(cls, data, crc):
        if crc == crc16(data):
            # bytecode не закодирован
            print("## device bytecode is not encoded")
            return data

        for sn in cls.serial_numbers():
            print(f'try sn: {sn:>5} \r', end='')
            r = decode_ipr_v1(data, crc, sn)
            if r is not None:
                print(f"## device bytecode is encoded (sn: {sn})")
                return r

            if cls.brute_quick:
                if not decode_ipr_v2_quick_check(data, crc, sn, offset=0):
                    continue

            r = decode_ipr_v2(data, crc, sn)
            if r is not None:
                print(f"## device bytecode is DES encoded (sn: {sn})")
                return r

            r = decode_ipr_v2(data, crc, sn, 0xB33506FB)
            if r is not None:
                print(f"## device bytecode is DES (777) encoded (sn: {sn})")
                return r

        print("## bad bytecode or unknown encoding")
        return None

    @classmethod
    def decode_cal_bytecode(cls, data):
        data_len = len(data)
        if data_len < 32+2:  # minimum 1 block +2 bytes crc
            print('## data size is too small, the file is corrupted')
            return None
        data_len = 32 * (data_len // 32) - 32
        _data = data[:data_len]
        _pad = data[data_len:]
        crc = _pad[0] << 8 | _pad[1]
        if len(_pad) != 32:
            print('## data size is not a multiple of 32, the file is probably corrupted')

        cls.detected_sn = []
        for sn in cls.serial_numbers():
            print(f'try sn: {sn:>5} \r', end='')
            r = decode_cal(_data, crc, sn, cls.brute_quick)
            if r is not None:
                print(f"## calculator bytecode is encoded (sn: {sn})")
                return r

        print("## bad bytecode or unknown encoding")
        return None

    @classmethod
    def encode_cal_bytecode(cls, data, sn):
        data = encode_cal(data, sn)
        return '\n'.join(data[p:p + 32].hex().upper() for p in range(0, len(data), 32)) + '\n'


def crc16(data):
    crc = 0xFFFF
    for i in range(len(data)):
        crc ^= data[i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x8408
            else:
                crc = crc << 1
    return crc & 0xFFFF


def crc16_1021(data):
    crc = 0xFFFF
    for i in range(len(data)):
        crc ^= data[i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def decode_ipr_v1(data, crc, sn):
    # Закодирован
    # v1
    length = len(data)
    tbl1 = (0x11, 0x22, 0x33, 0x14, 0x25, 0x36, 0x17, 0x28, 0x39, 0x1A, 0x2B, 0x3C, 0x1D, 0x2E, 0x3F, 0x35)
    data2 = list(data)
    crcpad = [0] * 64
    crcpad[0] = crc >> 8
    crcpad[1] = crc & 0xFF
    data2 += crcpad

    # sn = get_sn()
    x = tbl1[sn & 0x0F]

    data2[length] ^= data2[0]
    data2[length+1] ^= data2[1]

    z = (sn >> 8) ^ sn ^ data2[length] ^ data2[length+1]

    buf = [0] * 64
    for p in range(0, length, 64):

        for i in range(64):
            buf[i ^ (x & 0xFF)] = data2[p + i] ^ (z & 0xFF)
            z += i
        for i in range(64):
            data2[p + i] = buf[i]

    crc2 = data2[-64] << 8 | data2[-63]
    data2 = bytearray(data2[:-64])
    if crc2 == crc16(data2):
        return data2
    else:
        return data2 if Decoder.ignore_check else None


def decode_ipr_v2(data, crc, sn, sub_key=0xA5A5A5A5):
    # Закодирован DES
    # v2

    def get_xyz(seed):
        result = 0
        for i in range(32):
            if seed & 0x80000000 == 0:
                result = (result ^ 0x8437A5BE) * 0x11
            else:
                result = (result * 0x0B) ^ (result * 0xB0000)
            seed <<= 1
        return result & 0xFFFFFFFF

    if len(data) % 8:
        return None

    # sn = get_sn()
    k = get_xyz(sn)

    # DES ECB
    key = struct.pack('>II', k, k ^ sub_key)

    dkeys = tuple(des.derive_keys(key))[::-1]
    tmp = []
    blocks = (struct.unpack(">Q", data[i: i + 8])[0] for i in range(0, len(data), 8))
    for block in blocks:
        tmp.append(des.encode_block(block, dkeys))
    decoded = bytearray(b''.join(struct.pack(">Q", block) for block in tmp))

    # Additional iprog decoding
    for i in range(len(decoded)):
        decoded[i] ^= k & 0xFF
        k += 1

    if crc == crc16(decoded):
        return decoded
    else:
        return decoded if Decoder.ignore_check else None


def decode_ipr_v2_quick_check(data, _crc, sn, sub_key=0xA5A5A5A5, offset=0):
    # Search pattern.
    # PUSHR  xx         5A xx
    # ENTER  yy, zz     5F yz
    # ...
    # Procs may start with a different pattern if they have no variables and arguments

    def get_xyz(seed):
        result = 0
        for i in range(32):
            if seed & 0x80000000 == 0:
                result = (result ^ 0x8437A5BE) * 0x11
            else:
                result = (result * 0x0B) ^ (result * 0xB0000)
            seed <<= 1
        return result & 0xFFFFFFFF

    maxblocks = 1 + (offset + 2) // 8
    k = get_xyz(sn)

    # DES ECB
    key = struct.pack('>II', k, k ^ sub_key)

    dkeys = tuple(des.derive_keys(key))[::-1]
    tmp = []
    blocks = (struct.unpack(">Q", data[i: i + 8])[0] for i in range(0, len(data), 8))
    for block in blocks:
        tmp.append(des.encode_block(block, dkeys))
        if len(tmp) >= maxblocks:
            break

    decoded = bytearray(b''.join(struct.pack(">Q", block) for block in tmp))

    # Additional iprog decoding
    for i in range(len(decoded)):
        decoded[i] ^= k & 0xFF
        k += 1

    if decoded[offset] == 0x5A and decoded[offset+1] < 32 and decoded[offset+2] == 0x5F:
        print(f'## possible sn: {sn}')
        return True
    else:
        return False


def decode_cal(data, crc, sn, quick_check=False):
    length = len(data)
    tbl1 = (0x1F, 0x0E, 0x1D, 0x0C, 0x1B, 0x0A, 0x19, 0x08, 0x17, 0x06, 0x15, 0x04, 0x13, 0x02, 0x11, 0x05)
    x = tbl1[sn & 0x0F]
    z = (x * ((sn >> 8) ^ sn) & 0xFF) ^ (crc >> 8) ^ (crc & 0xFF)
    z &= 0xFF
    buf = [0] * 32
    data2 = bytearray(data)
    for p in range(0, length, 32):
        for i in range(32):
            buf[i ^ x] = data2[p + i] ^ z
            z = (z + 0x55) & 0xFF

        if quick_check and p == 0:
            # быстрая проверка
            on_show = buf[1] << 8 | buf[0]
            on_apply = buf[3] << 8 | buf[2]
            on_change = buf[5] << 8 | buf[4]
            unused = buf[7] << 8 | buf[6]
            if ((on_show == 0xFFFF or on_show < length) and (on_apply == 0xFFFF or on_apply < length) and
                    (on_change == 0xFFFF or on_change < length) and (unused == 0xFFFF or unused < length)):
                # Похоже на допустимые значения
                pass
            else:
                # Недопустимые значения, дальше можно не распаковывать
                return None

        data2[p:p+32] = buf

    if crc == crc16_1021(data2):

        if Decoder.brute_all:
            Decoder.detected_sn.append(sn)
            print(f'matching sn: {sn}')
            return None

        return data2
    else:
        return data2 if Decoder.ignore_check else None


def encode_cal(binary, sn):
    length = len(binary)
    crc = crc16_1021(binary)
    tbl1 = (0x1F, 0x0E, 0x1D, 0x0C, 0x1B, 0x0A, 0x19, 0x08, 0x17, 0x06, 0x15, 0x04, 0x13, 0x02, 0x11, 0x05)
    x = tbl1[sn & 0x0F]
    z = ((x * ((sn >> 8) ^ sn)) ^ (crc >> 8) ^ crc) & 0xFF
    data2 = bytearray(length + 32)                  # additional 32-byte chunk for crc and garbage
    for p in range(0, length, 32):
        for i in range(32):
            data2[p + i] = binary[p+(i ^ x)] ^ z
            z = (z + 0x55) & 0xFF

    data2[length] = crc >> 8
    data2[length+1] = crc & 0xFF
    # data2[length + 2:] = random.randbytes(32-2)     # unnecessarily
    return data2
