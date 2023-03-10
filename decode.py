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

    M1 = [0] * 4
    M2 = []

    def getXYZ(key):
        result = 0
        for i in range(32):
            if key & 0x80000000 == 0:
                result = (result ^ 0x8437A5BE) * 0x11
            else:
                result = (result * 0x0B) ^ (result * 0xB0000)
            key <<= 1
        return result & 0xFFFFFFFF

    def byteswap(d):
        b0 = d >> 24
        b1 = d >> 16 & 0xFF
        b2 = d >> 8 & 0xFF
        b3 = d & 0xFF
        return b0 | b1 << 8 | b2 << 16 | b3 << 24

    def des_perm3():
        r2 = (M1[3] ^ (M1[2] >> 4)) & 0x0F0F0F0F
        M1[3] ^= r2
        M1[2] ^= r2 << 4

        r1 = 0x0000FFFF
        r2 = (M1[2] ^ (M1[3] >> 16)) & r1
        M1[2] ^= r2
        r12 = M1[3] ^ (r2 << 16)
        M1[3] = r12
        r3 = r12
        r12 = r12 ^ (M1[2] >> 2)
        r2 = 0x33333333
        r2 = r2 & r12
        r3 = r3 ^ r2
        M1[3] = r3

        r12 = M1[2] ^ (r2 << 2)
        M1[2] = r12
        r2 = M1[3]
        r3 = r12
        r12 = r12 ^ (r2 >> 16)
        r2 = r1 & r12
        r1 = r3 ^ r2
        M1[2] = r1

        M1[3] = M1[3] ^ (r2 << 16)

        r3 = 0x55555555
        r2 = M1[2]
        r1 = M1[3] ^ (r2 >> 1)
        r2 = r3 & r1
        M1[3] = M1[3] ^ r2
        r1 = M1[2] ^ (r2 << 1)
        M1[2] = r1
        r2 = M1[3]
        r12 = r1
        r1 = r1 ^ (r2 >> 8)
        r2 = 0x00FF00FF & r1
        M1[2] = r12 ^ r2
        r1 = M1[3] ^ (r2 << 8)
        M1[3] = r1
        r2 = M1[2]
        r12 = r1
        r1 = r1 ^ (r2 >> 1)
        r2 = r3 & r1
        r3 = r12 ^ r2
        M1[3] = r3
        r12 = M1[2] ^ (r2 << 1)
        M1[2] = r12
        r2 = r12
        r1 = M1[3]
        r3 = 0xF0
        r12 = r3 & (r1 >> 20)
        r2 = (r12 | (r2 << 8)) & 0xFFFFFFFF
        r1 = M1[3]
        r3 = 0xFF00000
        r12 = r3 & (r1 << 20)
        M1[2] = r12

        r12 = 0xFF000 & (M1[3] << 4)
        r1 = M1[2] | r12
        M1[2] = r1
        r3 = M1[3]

        r3 = M1[2] | (0x0FF0 & (r3 >> 12))
        M1[2] = r3
        M1[2] = r3 | (M1[3] >> 28)
        M1[3] = r2 >> 4

    def permutation():
        M1[2] = byteswap(M1[0])
        M1[3] = byteswap(M1[1])
        des_perm3()
        m2 = M1[2]  # r0
        m3 = M1[3]  # r1
        r2 = 0
        while True:
            m2 = (m2 >> 27 | m2 << 1) & 0xFFFFFFFF
            m3 = (m3 >> 27 | m3 << 1) & 0xFFFFFFFF
            while True:
                r9 = (0x24000000 & (m2 << 4)) | \
                     (0x10000000 & (m2 << 28)) | \
                     (0x08000000 & (m2 << 14)) | \
                     (0x02080000 & (m2 << 18)) | \
                     (0x01000000 & (m2 << 6)) | \
                     (0x00200000 & (m2 << 9)) | \
                     (0x00100000 & (m2 >> 1)) | \
                     (0x00040000 & (m2 << 10)) | \
                     (0x0020000 & (m2 << 2)) | \
                     (0x0010000 & (m2 >> 10)) | \
                     (0x0002000 & (m3 >> 13)) | \
                     (0x0001000 & (m3 >> 4)) | \
                     (0x0000800 & (m3 << 6)) | \
                     (0x0000400 & (m3 >> 1)) | \
                     (0x200 & (m3 >> 14)) | \
                     (m3 & 0x100) | \
                     (0x20 & (m3 >> 5)) | \
                     (0x10 & (m3 >> 10)) | \
                     (0x8 & (m3 >> 3)) | \
                     (0x4 & (m3 >> 18)) | \
                     (0x2 & (m3 >> 26)) | \
                     (0x1 & (m3 >> 24))
                M2.append(r9)

                r4 = 0x20000000 & (m2 << 15) | \
                     (0x10000000 & (m2 << 17)) | \
                     (0x8000000 & (m2 << 10)) | \
                     (0x4000000 & (m2 << 22)) | \
                     (0x2000000 & (m2 >> 2)) | \
                     (0x1000000 & (m2 << 1)) | \
                     (0x200000 & (m2 << 16)) | \
                     (0x100000 & (m2 << 11)) | \
                     (0x80000 & (m2 << 3)) | \
                     (0x40000 & (m2 >> 6)) | \
                     (0x20000 & (m2 << 15)) | \
                     (0x10000 & (m2 >> 4)) | \
                     (0x2000 & (m3 >> 2)) | \
                     (0x0808 & (m3 >> 14)) | \
                     (0x1000 & (m3 << 8)) | \
                     (0x400 & (m3 >> 9)) | \
                     (m3 & 0x200) | \
                     (0x100 & (m3 << 7)) | \
                     0x0020 & (m3 >> 7) | \
                     (0x11 & (m3 >> 3)) | \
                     ((m3 << 2) & 0x4) | \
                     0x02 & (m3 >> 21)
                M2.append(r4)

                r2 = r2 + 1
                if r2 >= 0x10:
                    return

                if r2 == 0 or r2 == 1 or r2 == 8 or r2 == 0x0f:
                    break
                m2 = (m2 << 2 | m2 >> 26) & 0xFFFFFFFF
                m3 = (m3 >> 26 | m3 << 2) & 0xFFFFFFFF

    def des_perm1():
        r12 = M1[2]
        r1 = M1[3]
        r2 = r1 ^ (r12 >> 4)
        r3 = 0x0F0F0F0F
        r1 = r3 & r2
        r12 = M1[3]
        r12 = r12 ^ r1
        M1[3] = r12

        r2 = M1[2]
        r2 = r2 ^ (r1 << 4)
        M1[2] = r2

        # 6ae4
        r3 = M1[3]
        r12 = r3 ^ (r2 >> 16)
        # r1 = (r12 << 16)
        # r1 = (r1 >> 16)
        r1 = r12 & 0x0000FFFF
        r2 = M1[3]
        r2 = r2 ^ r1
        M1[3] = r2

        r3 = M1[2]
        r3 = (r3 ^ (r1 << 16)) & 0xFFFFFFFF
        M1[2] = r3

        r1 = M1[3]
        r12 = r3
        r2 = r3 ^ (r1 >> 2)
        r3 = 0x33333333
        r1 = r3 & r2
        r12 = r12 ^ r1
        M1[2] = r12

        r2 = M1[3]
        r2 = (r2 ^ (r1 << 2)) & 0xFFFFFFFF
        M1[3] = r2

        r3 = M1[2]
        r12 = r3 ^ (r2 >> 8)
        r2 = 0x000000FF
        r2 = r2 | 0x00FF0000
        r1 = r2 & r12
        r3 = M1[2]
        r3 = r3 ^ r1
        M1[2] = r3

        r12 = M1[3]
        r12 = (r12 ^ (r1 << 8)) & 0xFFFFFFFF
        M1[3] = r12

        r1 = M1[2]
        r2 = r12
        r3 = r12 ^ (r1 >> 1)
        r12 = 0x55555555
        r1 = r12 & r3
        r2 = r2 ^ r1
        M1[3] = r2

        r3 = M1[2]
        r3 = (r3 ^ (r1 << 1)) & 0xFFFFFFFF
        M1[2] = r3

        r1 = (r3 >> 31 | r3 << 1) & 0xFFFFFFFF
        M1[2] = r1

        r3 = M1[3]
        r12 = (r3 >> 31 | r3 << 1) & 0xFFFFFFFF
        M1[3] = r12

    def des_perm2():
        t = M1[3]
        M1[3] = M1[2]
        M1[2] = t

        M1[2] = (M1[2] >> 1 | M1[2] << 31) & 0xFFFFFFFF
        M1[3] = (M1[3] >> 1 | M1[3] << 31) & 0xFFFFFFFF

        t = M1[3]
        t = 0x55555555 & (t ^ M1[2] >> 1)
        M1[3] = M1[3] ^ t

        t = (M1[2] ^ t << 1) & 0xFFFFFFFF
        M1[2] = t

        t = (t ^ M1[3] >> 8) & 0xff00ff
        M1[2] = M1[2] ^ t

        t = (M1[3] ^ t << 8) & 0xFFFFFFFF
        M1[3] = t

        t = 0x33333333 & (M1[2] ^ t >> 2)
        M1[2] = M1[2] ^ t

        t = (M1[3] ^ t << 2) & 0xFFFFFFFF
        M1[3] = t

        t = (t ^ M1[2] >> 0x10) & 0xffff
        M1[3] = M1[3] ^ t

        t = (M1[2] ^ t << 16) & 0xFFFFFFFF
        M1[2] = t

        t = 0x0F0F0F0F & (M1[3] ^ t >> 4)
        M1[3] = M1[3] ^ t
        M1[2] = (M1[2] ^ t << 4) & 0xFFFFFFFF

        t = M1[3]
        M1[3] = M1[2]
        M1[2] = t

    def cypher_xor(i):
        spfunction1 = [0x01010400, 0x00000000, 0x00010000, 0x01010404,
                       0x01010004, 0x00010404, 0x00000004, 0x00010000,
                       0x00000400, 0x01010400, 0x01010404, 0x00000400,
                       0x01000404, 0x01010004, 0x01000000, 0x00000004,
                       0x00000404, 0x01000400, 0x01000400, 0x00010400,
                       0x00010400, 0x01010000, 0x01010000, 0x01000404,
                       0x00010004, 0x01000004, 0x01000004, 0x00010004,
                       0x00000000, 0x00000404, 0x00010404, 0x01000000,
                       0x00010000, 0x01010404, 0x00000004, 0x01010000,
                       0x01010400, 0x01000000, 0x01000000, 0x00000400,
                       0x01010004, 0x00010000, 0x00010400, 0x01000004,
                       0x00000400, 0x00000004, 0x01000404, 0x00010404,
                       0x01010404, 0x00010004, 0x01010000, 0x01000404,
                       0x01000004, 0x00000404, 0x00010404, 0x01010400,
                       0x00000404, 0x01000400, 0x01000400, 0x00000000,
                       0x00010004, 0x00010400, 0x00000000, 0x01010004]
        spfunction2 = [0x80108020, 0x80008000, 0x00008000, 0x00108020,
                       0x00100000, 0x00000020, 0x80100020, 0x80008020,
                       0x80000020, 0x80108020, 0x80108000, 0x80000000,
                       0x80008000, 0x00100000, 0x00000020, 0x80100020,
                       0x00108000, 0x00100020, 0x80008020, 0x00000000,
                       0x80000000, 0x00008000, 0x00108020, 0x80100000,
                       0x00100020, 0x80000020, 0x00000000, 0x00108000,
                       0x00008020, 0x80108000, 0x80100000, 0x00008020,
                       0x00000000, 0x00108020, 0x80100020, 0x00100000,
                       0x80008020, 0x80100000, 0x80108000, 0x00008000,
                       0x80100000, 0x80008000, 0x00000020, 0x80108020,
                       0x00108020, 0x00000020, 0x00008000, 0x80000000,
                       0x00008020, 0x80108000, 0x00100000, 0x80000020,
                       0x00100020, 0x80008020, 0x80000020, 0x00100020,
                       0x00108000, 0x00000000, 0x80008000, 0x00008020,
                       0x80000000, 0x80100020, 0x80108020, 0x00108000]
        spfunction3 = [0x00000208, 0x08020200, 0x00000000, 0x08020008,
                       0x08000200, 0x00000000, 0x00020208, 0x08000200,
                       0x00020008, 0x08000008, 0x08000008, 0x00020000,
                       0x08020208, 0x00020008, 0x08020000, 0x00000208,
                       0x08000000, 0x00000008, 0x08020200, 0x00000200,
                       0x00020200, 0x08020000, 0x08020008, 0x00020208,
                       0x08000208, 0x00020200, 0x00020000, 0x08000208,
                       0x00000008, 0x08020208, 0x00000200, 0x08000000,
                       0x08020200, 0x08000000, 0x00020008, 0x00000208,
                       0x00020000, 0x08020200, 0x08000200, 0x00000000,
                       0x00000200, 0x00020008, 0x08020208, 0x08000200,
                       0x08000008, 0x00000200, 0x00000000, 0x08020008,
                       0x08000208, 0x00020000, 0x08000000, 0x08020208,
                       0x00000008, 0x00020208, 0x00020200, 0x08000008,
                       0x08020000, 0x08000208, 0x00000208, 0x08020000,
                       0x00020208, 0x00000008, 0x08020008, 0x00020200]
        spfunction4 = [0x00802001, 0x00002081, 0x00002081, 0x00000080,
                       0x00802080, 0x00800081, 0x00800001, 0x00002001,
                       0x00000000, 0x00802000, 0x00802000, 0x00802081,
                       0x00000081, 0x00000000, 0x00800080, 0x00800001,
                       0x00000001, 0x00002000, 0x00800000, 0x00802001,
                       0x00000080, 0x00800000, 0x00002001, 0x00002080,
                       0x00800081, 0x00000001, 0x00002080, 0x00800080,
                       0x00002000, 0x00802080, 0x00802081, 0x00000081,
                       0x00800080, 0x00800001, 0x00802000, 0x00802081,
                       0x00000081, 0x00000000, 0x00000000, 0x00802000,
                       0x00002080, 0x00800080, 0x00800081, 0x00000001,
                       0x00802001, 0x00002081, 0x00002081, 0x00000080,
                       0x00802081, 0x00000081, 0x00000001, 0x00002000,
                       0x00800001, 0x00002001, 0x00802080, 0x00800081,
                       0x00002001, 0x00002080, 0x00800000, 0x00802001,
                       0x00000080, 0x00800000, 0x00002000, 0x00802080]
        spfunction5 = [0x00000100, 0x02080100, 0x02080000, 0x42000100,
                       0x00080000, 0x00000100, 0x40000000, 0x02080000,
                       0x40080100, 0x00080000, 0x02000100, 0x40080100,
                       0x42000100, 0x42080000, 0x00080100, 0x40000000,
                       0x02000000, 0x40080000, 0x40080000, 0x00000000,
                       0x40000100, 0x42080100, 0x42080100, 0x02000100,
                       0x42080000, 0x40000100, 0x00000000, 0x42000000,
                       0x02080100, 0x02000000, 0x42000000, 0x00080100,
                       0x00080000, 0x42000100, 0x00000100, 0x02000000,
                       0x40000000, 0x02080000, 0x42000100, 0x40080100,
                       0x02000100, 0x40000000, 0x42080000, 0x02080100,
                       0x40080100, 0x00000100, 0x02000000, 0x42080000,
                       0x42080100, 0x00080100, 0x42000000, 0x42080100,
                       0x02080000, 0x00000000, 0x40080000, 0x42000000,
                       0x00080100, 0x02000100, 0x40000100, 0x00080000,
                       0x00000000, 0x40080000, 0x02080100, 0x40000100]
        spfunction6 = [0x20000010, 0x20400000, 0x00004000, 0x20404010,
                       0x20400000, 0x00000010, 0x20404010, 0x00400000,
                       0x20004000, 0x00404010, 0x00400000, 0x20000010,
                       0x00400010, 0x20004000, 0x20000000, 0x00004010,
                       0x00000000, 0x00400010, 0x20004010, 0x00004000,
                       0x00404000, 0x20004010, 0x00000010, 0x20400010,
                       0x20400010, 0x00000000, 0x00404010, 0x20404000,
                       0x00004010, 0x00404000, 0x20404000, 0x20000000,
                       0x20004000, 0x00000010, 0x20400010, 0x00404000,
                       0x20404010, 0x00400000, 0x00004010, 0x20000010,
                       0x00400000, 0x20004000, 0x20000000, 0x00004010,
                       0x20000010, 0x20404010, 0x00404000, 0x20400000,
                       0x00404010, 0x20404000, 0x00000000, 0x20400010,
                       0x00000010, 0x00004000, 0x20400000, 0x00404010,
                       0x00004000, 0x00400010, 0x20004010, 0x00000000,
                       0x20404000, 0x20000000, 0x00400010, 0x20004010]
        spfunction7 = [0x00200000, 0x04200002, 0x04000802, 0x00000000,
                       0x00000800, 0x04000802, 0x00200802, 0x04200800,
                       0x04200802, 0x00200000, 0x00000000, 0x04000002,
                       0x00000002, 0x04000000, 0x04200002, 0x00000802,
                       0x04000800, 0x00200802, 0x00200002, 0x04000800,
                       0x04000002, 0x04200000, 0x04200800, 0x00200002,
                       0x04200000, 0x00000800, 0x00000802, 0x04200802,
                       0x00200800, 0x00000002, 0x04000000, 0x00200800,
                       0x04000000, 0x00200800, 0x00200000, 0x04000802,
                       0x04000802, 0x04200002, 0x04200002, 0x00000002,
                       0x00200002, 0x04000000, 0x04000800, 0x00200000,
                       0x04200800, 0x00000802, 0x00200802, 0x04200800,
                       0x00000802, 0x04000002, 0x04200802, 0x04200000,
                       0x00200800, 0x00000000, 0x00000002, 0x04200802,
                       0x00000000, 0x00200802, 0x04200000, 0x00000800,
                       0x04000002, 0x04000800, 0x00000800, 0x00200002]
        spfunction8 = [0x10001040, 0x00001000, 0x00040000, 0x10041040,
                       0x10000000, 0x10001040, 0x00000040, 0x10000000,
                       0x00040040, 0x10040000, 0x10041040, 0x00041000,
                       0x10041000, 0x00041040, 0x00001000, 0x00000040,
                       0x10040000, 0x10000040, 0x10001000, 0x00001040,
                       0x00041000, 0x00040040, 0x10040040, 0x10041000,
                       0x00001040, 0x00000000, 0x00000000, 0x10040040,
                       0x10000040, 0x10001000, 0x00041040, 0x00040000,
                       0x00041040, 0x00040000, 0x10041000, 0x00001000,
                       0x00000040, 0x10040040, 0x00001000, 0x00041040,
                       0x10001000, 0x00000040, 0x10000040, 0x10040000,
                       0x10040040, 0x10000000, 0x00040000, 0x10001040,
                       0x00000000, 0x10041040, 0x00040040, 0x10000040,
                       0x10040000, 0x10001000, 0x10001040, 0x00000000,
                       0x10041040, 0x00041000, 0x00041000, 0x00001040,
                       0x00001040, 0x00040040, 0x10000000, 0x10041000]

        v1 = M2[i] ^ M1[3]
        M1[2] ^= spfunction2[v1 >> 24 & 0x3F]
        M1[2] ^= spfunction4[v1 >> 16 & 0x3F]
        M1[2] ^= spfunction6[v1 >> 8 & 0x3F]
        M1[2] ^= spfunction8[v1 & 0x3F]

        v1 = ((M1[3] >> 4 | M1[3] << 28) & 0xFFFFFFFF) ^ M2[i + 1]
        M1[2] ^= spfunction1[v1 >> 24 & 0x3F]
        M1[2] ^= spfunction3[v1 >> 16 & 0x3F]
        M1[2] ^= spfunction5[v1 >> 8 & 0x3F]
        M1[2] ^= spfunction7[v1 & 0x3F]

        t = M1[3]
        M1[3] = M1[2]
        M1[2] = t

    def des_decodeblock(dat, a):
        r0 = dat[a + 0]
        r1 = dat[a + 1]
        r2 = r1 << 16
        r3 = r2 | (r0 << 24)
        r12 = dat[a + 2]
        lr = r3 | (r12 << 8)
        r6 = dat[a + 3]
        r7 = r6 | lr
        M1[2] = r7

        r0 = dat[a + 4]
        r1 = dat[a + 5]
        r2 = r1 << 16
        r3 = r2 | (r0 << 24)
        r12 = dat[a + 6]
        lr = r3 | (r12 << 8)
        r6 = dat[a + 7]
        r7 = r6 | lr
        M1[3] = r7

        des_perm1()

        r6 = 30
        for _ in range(4):
            cypher_xor(r6)
            cypher_xor(r6 - 2)
            cypher_xor(r6 - 4)
            cypher_xor(r6 - 6)
            r6 = r6 - 8

        des_perm2()

        dat[a + 0] = M1[3] >> 24 & 0xFF
        dat[a + 1] = M1[3] >> 16 & 0xFF
        dat[a + 2] = M1[3] >> 8 & 0xFF
        dat[a + 3] = M1[3] & 0xFF
        dat[a + 4] = M1[2] >> 24 & 0xFF
        dat[a + 5] = M1[2] >> 16 & 0xFF
        dat[a + 6] = M1[2] >> 8 & 0xFF
        dat[a + 7] = M1[2] & 0xFF

        return dat


    datalen = len(data)
    data2 = list(data)

    k = getXYZ(getSN())

    M1[0] = byteswap(k)
    M1[1] = byteswap(k ^ 0xA5A5A5A5)

    permutation()
    for i in range(0, datalen, 8):
        data2 = des_decodeblock(data2, i)

    for i in range(datalen):
        data2[i] ^= k & 0xFF
        k += 1

    data2 = bytearray(data2)
    if crc == crc16(data2):
        return data2
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
