import random
from typing import ByteString

from .b64 import encode as b64_encode, SYMBOLS as BASE64_SYMBOLS
from .salt import Salt
from .crypt import Crypt


class CryptMD5(Crypt):

    SALT_PREFIX = "$1$"
    ROUNDS = 1000
    MAX_SALT_LENGTH = 8

    def _do_crypt(self, plaintext: ByteString, salt: ByteString) -> ByteString:
        # start sum A
        a = self.method.hash_provider()
        digest_length = a.algorithm.digest_size

        # add the KEY string
        a.update(plaintext)

        # add the salt prefix
        a.update(self.SALT_PREFIX.encode(self.ENCODING))

        # last part is the SALT string
        a.update(salt)

        # start sum B
        b = self.method.hash_provider()

        # add the KEY
        b.update(plaintext)

        # add the SALT
        b.update(salt)

        # add the KEY again
        b.update(plaintext)

        # compute sum B
        sum_b = b.finalize()

        # for every character in the KEY, add one byte of sum B to A
        for _ in range(len(plaintext) // digest_length):
            a.update(sum_b)

        a.update(sum_b[0:len(plaintext) % digest_length])

        # The original implementation now does something weird: for every 1
        # bit in the key the first 0 is added to the buffer, for every 0 bit
        # the first character of the key.  This does not seem to be what was
        # intended but we have to follow this to be compatible.
        zero = b'\0'
        length = len(plaintext)
        while length != 0:
            if (length & 1) != 0:
                a.update(zero)
            else:
                a.update(plaintext[0:1])
            length >>= 1

        # compute sum A
        sum_a = a.finalize()

        # loop with just processes the output of each round to increase computational effort
        ac = sum_a
        for i in range(self.ROUNDS):
            c = self.method.hash_provider()
            if i % 2 != 0:
                # for all odd rounds, add in KEY
                c.update(plaintext)
            else:
                # for all even rounds, add in result of previous round
                c.update(ac)

            if i % 3 != 0:
                # for all rounds not divisible by 3, add in SALT
                c.update(salt)

            if i % 7 != 0:
                # for all rounds not divisible by 7, add in result of previous round
                c.update(plaintext)

            if i % 2 != 0:
                # for all odd rounds, add in result of previous round
                c.update(ac)
            else:
                # for all even rounds, add in KEY
                c.update(plaintext)

            # compute intermediate sum
            ac = c.finalize()

        return ac

    def _crypt(self, plaintext: str, salt: Salt) -> str:
        ciphertext = self._do_crypt(plaintext.encode(self.ENCODING), salt.bytes(self.MAX_SALT_LENGTH, self.ENCODING))
        return self._password_to_string(ciphertext, salt, self.MAX_SALT_LENGTH)

    def _generate_salt(self, rounds=None) -> str:
        salt = "".join(random.choices(BASE64_SYMBOLS, k=self.MAX_SALT_LENGTH))
        return f"{self.SALT_PREFIX}{salt}"

    def _encode_parameters(self, params) -> str:
        raise NotImplementedError()

    def _encode_password(self, ciphertext: ByteString) -> str:
        s = b64_encode(ciphertext[0], ciphertext[6], ciphertext[12], 4)
        s += b64_encode(ciphertext[1], ciphertext[7], ciphertext[13], 4)
        s += b64_encode(ciphertext[2], ciphertext[8], ciphertext[14], 4)
        s += b64_encode(ciphertext[3], ciphertext[9], ciphertext[15], 4)
        s += b64_encode(ciphertext[4], ciphertext[10], ciphertext[5], 4)
        s += b64_encode(0, 0, ciphertext[11], 2)
        return s
