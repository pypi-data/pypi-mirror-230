import random
from abc import abstractmethod
from typing import ByteString, Optional

from .b64 import SYMBOLS as B64_SYMBOLS
from .crypt import Crypt
from .salt import Salt


class CryptSHA2(Crypt):

    SALT_PREFIX = None
    MAX_SALT_LENGTH = 32
    ROUNDS_PARAM = "rounds="
    MIN_ROUNDS = 1_000
    MAX_ROUNDS = 999_999_999
    DEFAULT_ROUNDS = 5000

    def _rounds(self, salt: Salt) -> Optional[int]:
        if not salt.params or not salt.params.startswith(self.ROUNDS_PARAM):
            return None
        rounds = int(salt.params[len(self.ROUNDS_PARAM):])
        return min(self.MAX_ROUNDS, max(self.MIN_ROUNDS, rounds))

    def _make_sequence(self, sum: ByteString, length: int, digest_length: int) -> ByteString:
        buf = bytearray()
        for _ in range(length // digest_length):
            buf.extend(sum)
        buf.extend(sum[0:length % digest_length])
        return bytes(buf)

    def _do_crypt(self, plaintext: ByteString, salt: ByteString, rounds: int) -> ByteString:
        # 1. start digest A
        a = self.method.hash_provider()

        # 2. the password string is added to digest A
        a.update(plaintext)

        # 3. the salt string is added to digest A
        a.update(salt)

        # 4. start digest B
        b = self.method.hash_provider()

        # 5. add the password to digest B
        b.update(plaintext)

        # 6. add the salt to digest B
        b.update(salt)

        # 7. add the password again to digest B
        b.update(plaintext)

        # 8. finish digest B
        sum_b = b.finalize()

        # 9. For each block of 32 or 64 bytes in the password string, add digest B to digest A
        digest_length = a.algorithm.digest_size
        for _ in range(len(plaintext) // digest_length):
            a.update(sum_b)

        # 10. For the remaining N bytes of the password string add the first
        #     N bytes of digest B to digest A
        a.update(sum_b[0:len(plaintext) % digest_length])

        # 11. For each bit of the binary representation of the length of the
        #     password string up to and including the highest 1-digit, starting
        #     from to lowest bit position (numeric value 1):
        #     a) for a 1-digit add digest B to digest A
        #     b) for a 0-digit add the password string
        length = len(plaintext)
        while length > 0:
            if (length & 0x1) != 0:
                a.update(sum_b)
            else:
                a.update(plaintext)
            length >>= 1

        # 12. finish digest A
        sum_a = a.finalize()

        # 13. start digest DP
        dp = self.method.hash_provider()

        # 14. for every byte in the password, add the password to digest DP
        for _ in range(len(plaintext)):
            dp.update(plaintext)

        # 15. finish digest DP
        sum_dp = dp.finalize()

        # 16. produce byte sequence P of the same length as the password where
        #     a) for each block of 32 or 64 bytes of length of the password string
        #        the entire digest DP is used
        #     b) for the remaining N (up to  31 or 63) bytes use the first N
        #        bytes of digest DP
        seq_p = self._make_sequence(sum_dp, len(plaintext), digest_length)

        # 17. start digest DS
        ds = self.method.hash_provider()

        # 18. repeat the following 16+A[0] times, where A[0] represents the first
        #     byte in digest A interpreted as an 8-bit unsigned value: add the salt to digest DS
        for _ in range(16 + (sum_a[0] & 0xff)):
            ds.update(salt)

        # 19. finish digest DS
        sum_ds = ds.finalize()

        #  20. produce byte sequence S of the same length as the salt string where
        #      a) for each block of 32 or 64 bytes of length of the salt string
        #         the entire digest DS is used
        #      b) for the remaining N (up to  31 or 63) bytes use the first N
        #         bytes of digest DS
        seq_s = self._make_sequence(sum_ds, len(salt), digest_length)

        #  21. repeat a loop according to the number specified in the rounds=<N>
        #      specification in the salt (or the default value if none is
        #      present).  Each round is numbered, starting with 0 and up to N-1.
        #
        #      The loop uses a digest as input.  In the first round it is the
        #      digest produced in step 12.  In the latter steps it is the digest
        #      produced in step 21.h.  The following text uses the notation
        #      "digest A/C" to describe this behavior.

        ac = sum_a
        for i in range(rounds):
            # a. start digest C
            c = self.method.hash_provider()

            if i % 2 != 0:
                # b. for odd rounds, add sequence P to digest C
                c.update(seq_p)
            else:
                # c. for even rounds, add digest A/C to digest C
                c.update(ac)

            if i % 3 != 0:
                # d. for all round numbers not divisible by 3, add sequence S to digest C
                c.update(seq_s)

            if i % 7 != 0:
                # e. for all round numbers not divisible by 7, add sequence P to digest C
                c.update(seq_p)

            if i % 2 != 0:
                # f. for odd rounds add digest A/C to digest C
                c.update(ac)
            else:
                # g. for even rounds add sequence P to digest C
                c.update(seq_p)

            # h. finish digest C
            ac = c.finalize()

        return ac

    def _crypt(self, plaintext: str, salt: Salt) -> str:
        rounds = self._rounds(salt)
        ciphertext = self._do_crypt(plaintext.encode(self.ENCODING),
                                    salt.bytes(self.MAX_SALT_LENGTH, self.ENCODING),
                                    rounds if rounds else self.DEFAULT_ROUNDS)
        return self._password_to_string(ciphertext, salt, self.MAX_SALT_LENGTH, rounds=rounds)

    def _generate_salt(self, rounds=None) -> str:
        prefix = self.SALT_PREFIX if not rounds or rounds == self.DEFAULT_ROUNDS else f"{self.SALT_PREFIX}{self.ROUNDS_PARAM}{rounds}$"
        salt = "".join(random.choices(B64_SYMBOLS, k=self.MAX_SALT_LENGTH))
        return f"{prefix}{salt}"

    @abstractmethod
    def _encode_password(self, ciphertext: ByteString) -> str:
        pass

    def _encode_parameters(self, params) -> str:
        return ",".join((f"{k}={str(v)}" for k, v in params.items() if v is not None))


