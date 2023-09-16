from typing import ByteString

from .b64 import encode as b64_encode

from .crypt_sha2 import CryptSHA2


class CryptSHA256(CryptSHA2):

    SALT_PREFIX = "$5$"

    def _encode_password(self, ciphertext: ByteString) -> str:
        s = b64_encode(ciphertext[0], ciphertext[10], ciphertext[20], 4)
        s += b64_encode(ciphertext[21], ciphertext[1], ciphertext[11], 4)
        s += b64_encode(ciphertext[12], ciphertext[22], ciphertext[2], 4)
        s += b64_encode(ciphertext[3], ciphertext[13], ciphertext[23], 4)
        s += b64_encode(ciphertext[24], ciphertext[4], ciphertext[14], 4)
        s += b64_encode(ciphertext[15], ciphertext[25], ciphertext[5], 4)
        s += b64_encode(ciphertext[6], ciphertext[16], ciphertext[26], 4)
        s += b64_encode(ciphertext[27], ciphertext[7], ciphertext[17], 4)
        s += b64_encode(ciphertext[18], ciphertext[28], ciphertext[8], 4)
        s += b64_encode(ciphertext[9], ciphertext[19], ciphertext[29], 4)
        s += b64_encode(0, ciphertext[31], ciphertext[30], 3)
        return s


