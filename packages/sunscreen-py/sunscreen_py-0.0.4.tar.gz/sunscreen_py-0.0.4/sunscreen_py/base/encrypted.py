from abc import ABC, abstractmethod
from .buffer import SunscreenBuffer, DEFAULT_BUFFER_LENGTH
from threading import RLock
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any, Union
from .rustlibrary import RustLibrary
import ctypes


class Encrypted(ABC):
    DEFAULT_ZERO_WORKAROUND = 0.000000000000001

    def __init__(
        self,
        buffer: ctypes.c_void_p,
        context: SunscreenFHEContext,
        is_fresh: bool,
        noise_budget: Optional[int],
        key_set_override: Optional[KeySet] = None,
    ):
        self.rust_library: RustLibrary = context.get_rust_library()
        self.pointer: Optional[ctypes.c_void_p] = buffer
        self.context: SunscreenFHEContext = context
        self.is_fresh: bool = is_fresh
        self.noise_budget: Optional[int] = noise_budget
        self.key_set_override: Optional[KeySet] = key_set_override
        self.lock = RLock()

    def __del__(self):
        if self.pointer:
            self.rust_library.get().release_cipher(self.pointer)

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            return self.pointer

    def release(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            pointer = self.get()
            self.pointer = None
            return pointer

    def replace_pointer(self, pointer: Any) -> None:
        with self.lock:
            if self.pointer:
                self.rust_library.get().release_cipher(self.pointer)
            self.pointer = pointer

    def get_cipher(self) -> SunscreenBuffer:
        pointer = self.get()
        if pointer:
            buffer = SunscreenBuffer.create_for_length(DEFAULT_BUFFER_LENGTH)
            self.rust_library.get().get_cipher_as_string(pointer, buffer.get())
            return buffer
        raise Exception("Pointer is null")

    @abstractmethod
    def decrypt(self) -> Union[float, int]:
        raise NotImplementedError("Decryption is not implemented for base class")

    @abstractmethod
    def refresh_cipher(self) -> None:
        raise NotImplementedError("Refresh Cipher is not implemented for base class")

    @abstractmethod
    def __add__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for base class")

    @abstractmethod
    def __radd__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for base class")

    @abstractmethod
    def __sub__(self, other) -> "Encrypted":
        raise NotImplementedError("Subtraction is not implemented for base class")

    @abstractmethod
    def __rsub__(self, other) -> "Encrypted":
        raise NotImplementedError("Subtraction is not implemented for base class")

    @abstractmethod
    def __mul__(self, other) -> "Encrypted":
        raise NotImplementedError("Multiplication is not implemented for base class")

    @abstractmethod
    def __rmul__(self, other) -> "Encrypted":
        raise NotImplementedError("Multiplication is not implemented for base class")

    @abstractmethod
    def __div__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for base class")

    @abstractmethod
    def __rdiv__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for base class")

    @abstractmethod
    def shape(self) -> list[int]:
        raise NotImplementedError("Shape is not implemented for base class")

    @classmethod
    def fix_zero_in_plain(cls, value) -> float:
        if value == 0:
            return Encrypted.DEFAULT_ZERO_WORKAROUND

        return value

    @classmethod
    def get_noise_budget_from_runtime(
        cls,
        context: SunscreenFHEContext,
        cipher: ctypes.c_void_p,
        key_set_override: Optional[KeySet] = None,
    ) -> Optional[int]:
        try:
            private_key = context.get_private_key(key_set_override)
            result = None
            if private_key:
                result = (
                    context.get_rust_library()
                    .get()
                    .get_noise_budget_for_cipher(
                        context.get_inner_context(),
                        private_key,
                        cipher,
                    )
                )
            return result
        except Exception as e:
            print(e)
            return None
