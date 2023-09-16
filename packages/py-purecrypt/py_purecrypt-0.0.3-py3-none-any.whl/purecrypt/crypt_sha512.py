from typing import ByteString

from .b64 import encode as b64_encode
from .crypt_sha2 import CryptSHA2


class CryptSHA512(CryptSHA2):

    SALT_PREFIX = "$6$"

    def _encode_password(self, ciphertext: ByteString) -> str:
        s = b64_encode(ciphertext[0], ciphertext[21], ciphertext[42], 4)
        s += b64_encode(ciphertext[22], ciphertext[43], ciphertext[1], 4)
        s += b64_encode(ciphertext[44], ciphertext[2], ciphertext[23], 4)
        s += b64_encode(ciphertext[3], ciphertext[24], ciphertext[45], 4)
        s += b64_encode(ciphertext[25], ciphertext[46], ciphertext[4], 4)
        s += b64_encode(ciphertext[47], ciphertext[5], ciphertext[26], 4)
        s += b64_encode(ciphertext[6], ciphertext[27], ciphertext[48], 4)
        s += b64_encode(ciphertext[28], ciphertext[49], ciphertext[7], 4)
        s += b64_encode(ciphertext[50], ciphertext[8], ciphertext[29], 4)
        s += b64_encode(ciphertext[9], ciphertext[30], ciphertext[51], 4)
        s += b64_encode(ciphertext[31], ciphertext[52], ciphertext[10], 4)
        s += b64_encode(ciphertext[53], ciphertext[11], ciphertext[32], 4)
        s += b64_encode(ciphertext[12], ciphertext[33], ciphertext[54], 4)
        s += b64_encode(ciphertext[34], ciphertext[55], ciphertext[13], 4)
        s += b64_encode(ciphertext[56], ciphertext[14], ciphertext[35], 4)
        s += b64_encode(ciphertext[15], ciphertext[36], ciphertext[57], 4)
        s += b64_encode(ciphertext[37], ciphertext[58], ciphertext[16], 4)
        s += b64_encode(ciphertext[59], ciphertext[17], ciphertext[38], 4)
        s += b64_encode(ciphertext[18], ciphertext[39], ciphertext[60], 4)
        s += b64_encode(ciphertext[40], ciphertext[61], ciphertext[19], 4)
        s += b64_encode(ciphertext[62], ciphertext[20], ciphertext[41], 4)
        s += b64_encode(0, 0, ciphertext[63], 2)
        return s

