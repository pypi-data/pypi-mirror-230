from abc import ABC, abstractmethod
from typing import ByteString

from .method import Method
from .salt import Salt


class Crypt(ABC):

    ENCODING = "UTF-8"

    def __init__(self, method: Method):
        self.method = method

    @classmethod
    def for_method(cls, method: Method) -> "Crypt":
        provider_class = method.provider_class()
        return provider_class(method)

    @classmethod
    def generate_salt(cls, method: Method, rounds: int = None):
        return cls.for_method(method)._generate_salt(rounds)

    @classmethod
    def encrypt(cls, plaintext: str, salt: str):
        s = Salt(salt)
        return cls.for_method(Method.for_salt(s))._crypt(plaintext, s)

    @classmethod
    def is_valid(cls, plaintext: str, expected_ciphertext: str):
        ciphertext = cls.encrypt(plaintext, expected_ciphertext)
        return ciphertext == expected_ciphertext

    @abstractmethod
    def _generate_salt(self, rounds=None) -> str:
        pass

    @abstractmethod
    def _crypt(self, plaintext: str, salt: Salt) -> str:
        pass

    @abstractmethod
    def _encode_password(self, ciphertext: ByteString) -> str:
        pass

    @abstractmethod
    def _encode_parameters(self, params) -> str:
        pass

    def _password_to_string(self, ciphertext: ByteString, salt: Salt, max_salt_length: int, **params):
        s = f"${salt.type}$"
        if params:
            p = self._encode_parameters(params)
            if p:
                s += f"{p}$"
        s += f"{salt.bytes(max_salt_length, self.ENCODING).decode(self.ENCODING)}$"
        s += self._encode_password(ciphertext)
        return s

