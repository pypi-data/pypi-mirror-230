
SYMBOLS = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(b2: int, b1: int, b0: int, n: int):
    buf = ""
    w = ((b2 & 0xff) << 16) | ((b1 & 0xff) << 8) | (b0 & 0xff)

    for _ in range(n):
        buf += SYMBOLS[w & 0x3f]
        w >>= 6

    return buf
