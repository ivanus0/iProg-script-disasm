import struct
import des


def crc16(data: bytearray):
    crc = 0xFFFF
    for i in range(len(data)):
        crc ^= data[i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x8408
            else:
                crc = crc << 1
    return crc & 0xFFFF


def crc16_1021(data: bytearray):
    crc = 0xFFFF
    for i in range(len(data)):
        crc ^= data[i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def getSN():
    sn_encoded = 0x69EB7BDF  # sn == 1
    # sn_encoded = 0x23b9318D     # sn == 19
    # sn_encoded = 0x0f6bd109     # sn == 777 ?? не сходится...
    # sn_encoded = 0x79a96b9d     # sn == 777

    # sn_encoded = 0x0f6b
    # sn_encoded = ((sn_encoded ^ 0x1234) << 16) | sn_encoded
    if (sn_encoded >> 0x10 ^ sn_encoded) & 0xFFFF == 0x1234:
        result = sn_encoded & 0xFFFF
        for n in range(0x10):
            if (sn_encoded & 1) == 0:
                result = (result << 1) ^ 0x8021
            else:
                result <<= 1
            sn_encoded >>= 1
        return result & 0xFFFF
    else:
        return 0xFFFF


def decode_devicebytecode(data, crc):
    if crc == crc16(data):
        # bytecode не закодирован
        print("## device bytecode is not encoded")
        return data

    r = decode_v1(data, crc)
    if r is not None:
        print("## device bytecode is encoded v1")
        return r

    r = decode_v2(data, crc)
    if r is not None:
        print(f"## device bytecode is DES encoded (iprog sn={getSN()})")
        return r

    print("bad bytecode or unknown encoding")
    return None


def decode_v1(data, crc):
    # Закодирован
    # v1
    tbl1 = [0x11, 0x22, 0x33, 0x14, 0x25, 0x36, 0x17, 0x28, 0x39, 0x1A, 0x2B, 0x3C, 0x1D, 0x2E, 0x3F, 0x35]
    datalen = len(data)
    data2 = list(data)
    crcpad = [0] * 64
    crcpad[0] = crc >> 8
    crcpad[1] = crc & 0xFF
    data2 += crcpad

    sn = getSN()
    X = tbl1[sn & 0x0F]

    data2[datalen] ^= data2[0]
    data2[datalen+1] ^= data2[1]

    Z = (sn >> 8) ^ sn ^ data2[datalen] ^ data2[datalen+1]

    buf = [0] * 64
    for p in range(0, datalen, 64):

        for i in range(64):
            buf[i ^ (X & 0xFF)] = data2[p + i] ^ (Z & 0xFF)
            Z += i
        for i in range(64):
            data2[p + i] = buf[i]

    crc2 = data2[-64] << 8 | data2[-63]
    data2 = bytearray(data2[:-64])
    if crc2 == crc16(data2):
        return data2
    else:
        return None


def decode_v2(data, crc):
    # Закодирован DES
    # v2

    def getXYZ(key):
        result = 0
        for i in range(32):
            if key & 0x80000000 == 0:
                result = (result ^ 0x8437A5BE) * 0x11
            else:
                result = (result * 0x0B) ^ (result * 0xB0000)
            key <<= 1
        return result & 0xFFFFFFFF

    if len(data) % 8:
        return None

    k = getXYZ(getSN())

    # DES ECB
    key = struct.pack('>II', k, k ^ 0xA5A5A5A5)

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
        return None


def decode_cal(data):
    # декодер .cal
    tbl1 = [0x1F, 0x0E, 0x1D, 0x0C, 0x1B, 0x0A, 0x19, 0x08, 0x17, 0x06, 0x15, 0x04, 0x13, 0x02, 0x11, 0x05]
    datalen = len(data)-32
    # размер data должен быть кратен 32байт
    if datalen % 32:
        # Для декомпиляции некодированного дампа
        return bytearray(data)

    # data2 = list(data)
    sn = getSN()
    X = tbl1[sn & 0x0F]
    Z = (X * ((sn >> 8) ^ sn) & 0xFF) ^ data[datalen] ^ data[datalen + 1]
    buf = [0] * 32
    data2 = data[:datalen]
    for p in range(0, datalen, 32):

        for i in range(32):
            buf[i ^ X] = data2[p + i] ^ (Z & 0xFF)
            Z = (Z + 0x55) & 0xFFFFFFFF
        for i in range(32):
            data2[p + i] = buf[i]

    crc = data[datalen] << 8 | data[datalen + 1]
    if crc == crc16_1021(data2):
        return bytearray(data2)
    else:
        # Для декомпиляции некодированного дампа
        return bytearray(data)
