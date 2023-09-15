from .buffer import SunscreenBuffer
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any
import ctypes


class EncryptedSigned(Encrypted):
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
    ) -> "EncryptedSigned":
        cipher = (
            context.get_rust_library()
            .get()
            .encrypt_signed(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                number,
            )
        )

        if EncryptedSigned.standard_noise_for_fresh_cipher is None:
            EncryptedSigned.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, cipher, key_set_override
                )
            )

        result = EncryptedSigned(
            cipher,
            context,
            True,
            EncryptedSigned.standard_noise_for_fresh_cipher,
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
    ) -> "EncryptedSigned":
        cipher = (
            context.get_rust_library().get().get_cipher_from_string(cipher_obj.get())
        )
        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher, key_set_override
            )
        return EncryptedSigned(
            cipher, context, is_fresh, noise_budget, key_set_override
        )

    @classmethod
    def create_from_encrypted_cipher_pointer(
        cls,
        cipher: ctypes.c_void_p,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedSigned":
        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher, key_set_override
            )
        return EncryptedSigned(
            cipher, context, is_fresh, noise_budget, key_set_override
        )

    def refresh_cipher(self):
        value = self.decrypt()
        reencrypted = EncryptedSigned.create_from_plain(
            value, self.context, self.key_set_override
        )
        self.replace_pointer(reencrypted.release())
        self.noise_budget = reencrypted.noise_budget
        self.is_fresh = True

    def decrypt(self) -> int:
        return self.rust_library.get().decrypt_signed(
            self.context.get_inner_context(),
            self.context.get_private_key(self.key_set_override),
            self.get(),
        )

    def shape(self):
        return [1, 1]

    def __add__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for signed class")

    def __radd__(self, other) -> "Encrypted":
        raise NotImplementedError("Addition is not implemented for signed class")

    def __sub__(self, other) -> "Encrypted":
        raise NotImplementedError("Subtraction is not implemented for signed class")

    def __rsub__(self, other) -> "Encrypted":
        raise NotImplementedError("Subtraction is not implemented for signed class")

    def __mul__(self, other) -> "Encrypted":
        raise NotImplementedError("Multiplication is not implemented for signed class")

    def __rmul__(self, other) -> "Encrypted":
        raise NotImplementedError("Multiplication is not implemented for signed class")

    def __div__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for signed class")

    def __rdiv__(self, other) -> "Encrypted":
        raise NotImplementedError("Division is not implemented for signed class")

    @classmethod
    def __check_if_zero__(cls, value):
        if isinstance(value, EncryptedSignedZero) or (
            (isinstance(value, int)) and int(value) == 0
        ):
            return True
        return False


class EncryptedSignedZero(EncryptedSigned):
    def __init__(
        self, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ):
        EncryptedSigned.__init__(
            self,
            None,
            context,
            True,
            EncryptedSigned.standard_noise_for_fresh_cipher,
            key_set_override,
        )
        if EncryptedSigned.standard_noise_for_fresh_cipher is None:
            self.pointer = self.rust_library.get().encrypt_signed(
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                0,
            )
            EncryptedSigned.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, self.pointer, key_set_override
                )
            )
            self.noise_budget = EncryptedSigned.standard_noise_for_fresh_cipher

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            if not self.pointer:
                self.pointer = self.rust_library.get().encrypt_signed(
                    self.context.get_inner_context(),
                    self.context.get_public_key(self.key_set_override),
                    0,
                )

            return self.pointer
