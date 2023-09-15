from .buffer import SunscreenBuffer, DEFAULT_BUFFER_LENGTH
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any
import ctypes


class EncryptedUnsigned256(Encrypted):
    standard_noise_for_fresh_cipher = None

    def __init__(
        self,
        pointer: Any,
        context: SunscreenFHEContext,
        is_fresh: bool,
        noise_budget: Optional[int],
        key_set_override: Optional[KeySet],
    ):
        Encrypted.__init__(
            self, pointer, context, is_fresh, noise_budget, key_set_override
        )

    @classmethod
    def create_from_plain(
        cls,
        number: int,
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned256":
        encoded_bytes = number.to_bytes(32, byteorder="big")
        buffer = SunscreenBuffer.create_from_bytes(bytearray(encoded_bytes))
        cipher = (
            context.get_rust_library()
            .get()
            .encrypt_unsigned256(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                buffer.get(),
            )
        )

        if EncryptedUnsigned256.standard_noise_for_fresh_cipher is None:
            EncryptedUnsigned256.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, cipher, key_set_override
                )
            )

        result = EncryptedUnsigned256(
            cipher,
            context,
            True,
            EncryptedUnsigned256.standard_noise_for_fresh_cipher,
            key_set_override,
        )
        return result

    @classmethod
    def create_from_encrypted_cipher(
        cls,
        cipher_obj: SunscreenBuffer,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned256":
        cipher_ptr = (
            context.get_rust_library().get().get_cipher_from_string(cipher_obj.get())
        )

        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher_ptr, key_set_override
            )

        return EncryptedUnsigned256(
            cipher_ptr, context, is_fresh, noise_budget, key_set_override
        )

    @classmethod
    def create_from_encrypted_cipher_pointer(
        cls,
        cipher: Any,  # type: ignore
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned256":
        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher, key_set_override
            )

        return EncryptedUnsigned256(
            cipher, context, is_fresh, noise_budget, key_set_override
        )

    def refresh_cipher(self):
        value = self.decrypt()
        reencrypted = EncryptedUnsigned256.create_from_plain(
            value, self.context, self.key_set_override
        )
        self.replace_pointer(reencrypted.release())
        self.noise_budget = reencrypted.noise_budget
        self.is_fresh = True

    def decrypt(self) -> int:
        decrypt_buffer = SunscreenBuffer.create_for_length(DEFAULT_BUFFER_LENGTH)
        self.rust_library.get().decrypt_unsigned256(
            self.context.get_inner_context(),
            self.context.get_private_key(self.key_set_override),
            self.get(),
            decrypt_buffer.get(),
        )

        return int.from_bytes(decrypt_buffer.get_bytes(), byteorder="big")

    def shape(self) -> list[int]:
        return [1, 1]

    def __add__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for unsigned256 class")

    def __radd__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for unsigned256 class")

    def __sub__(self, other) -> "Encrypted":
        raise NotImplementedError(
            "Subtraction is not implemented for unsigned256 class"
        )

    def __rsub__(self, other) -> "Encrypted":
        raise NotImplementedError(
            "Subtraction is not implemented for unsigned256 class"
        )

    def __mul__(self, other) -> "Encrypted":
        raise NotImplementedError(
            "Multiplication is not implemented for unsigned256 class"
        )

    def __rmul__(self, other) -> "Encrypted":
        raise NotImplementedError(
            "Multiplication is not implemented for unsigned256 class"
        )

    def __div__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for unsigned256 class")

    def __rdiv__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for unsigned256 class")


class EncryptedUnsigned256Zero(EncryptedUnsigned256):
    def __init__(
        self, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ):
        EncryptedUnsigned256.__init__(
            self,
            None,
            context,
            True,
            EncryptedUnsigned256.standard_noise_for_fresh_cipher,
            key_set_override,
        )
        if EncryptedUnsigned256.standard_noise_for_fresh_cipher is None:
            self.pointer = EncryptedUnsigned256Zero.__create_ptr__(
                context, key_set_override
            )
            EncryptedUnsigned256.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, self.pointer, key_set_override
                )
            )
            self.noise_budget = EncryptedUnsigned256.standard_noise_for_fresh_cipher

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            if not self.pointer:
                self.pointer = EncryptedUnsigned256Zero.__create_ptr__(
                    self.context, self.key_set_override
                )

            return self.pointer

    @classmethod
    def __create_ptr__(
        cls, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ) -> ctypes.c_void_p:
        encoded_bytes = int(0).to_bytes(32, byteorder="big")
        buffer = SunscreenBuffer.create_from_bytes(bytearray(encoded_bytes))
        return (
            context.get_rust_library()
            .get()
            .encrypt_unsigned256(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                buffer.get(),
            )
        )
