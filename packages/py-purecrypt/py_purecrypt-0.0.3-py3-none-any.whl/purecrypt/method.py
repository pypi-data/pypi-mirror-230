from enum import Enum

import cryptography.hazmat.primitives.hashes as hashes

from .salt import Salt


class Method(Enum):
    MD5 = 1
    SHA256 = 5
    SHA512 = 6

    @classmethod
    def value_of(cls, s):
        s = s.upper()
        for method in Method:
            if method.name == s:
                return method
        raise ValueError(f"unrecognized method '{s}'")

    @classmethod
    def for_salt(cls, salt: Salt):
        for method in cls:
            if method.value == salt.type:
                return method
        raise ValueError(f"unrecognized salt type: {salt.type}")

    def hash_provider(self) -> hashes.Hash:
        if self is self.MD5:
            return hashes.Hash(hashes.MD5())
        elif self is self.SHA256:
            return hashes.Hash(hashes.SHA256())
        elif self is self.SHA512:
            return hashes.Hash(hashes.SHA512())
        raise TypeError(f"unimplemented method: {self}")

    def provider_class(self):
        from .crypt_md5 import CryptMD5
        from .crypt_sha256 import CryptSHA256
        from .crypt_sha512 import CryptSHA512

        if self is self.MD5:
            return CryptMD5
        elif self is self.SHA256:
            return CryptSHA256
        elif self is self.SHA512:
            return CryptSHA512
        raise TypeError(f"unimplemented method: {self}")

