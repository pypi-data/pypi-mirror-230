from ..internal.sunscreenpool import SunscreenPool
from .buffer import SunscreenBuffer
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any, Union
import ctypes


class EncryptedFloat64(Encrypted):
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
        number: float,
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloat64":
        cipher = (
            context.get_rust_library()
            .get()
            .encrypt_float(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                number,
            )
        )
        if EncryptedFloat64.standard_noise_for_fresh_cipher is None:
            EncryptedFloat64.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, cipher, key_set_override
                )
            )

        result = EncryptedFloat64(
            cipher,
            context,
            True,
            EncryptedFloat64.standard_noise_for_fresh_cipher,
            key_set_override,
        )
        return result

    @classmethod
    def create_from_encrypted_cipher(
        cls,
        cipher_bytes: SunscreenBuffer,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloat64":
        cipher = (
            context.get_rust_library().get().get_cipher_from_string(cipher_bytes.get())
        )
        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher, key_set_override
            )

        return EncryptedFloat64(
            cipher, context, is_fresh, noise_budget, key_set_override
        )

    @classmethod
    def create_from_encrypted_cipher_pointer(
        cls,
        cipher: Any,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloat64":
        if not noise_budget:
            noise_budget = Encrypted.get_noise_budget_from_runtime(
                context, cipher, key_set_override
            )
        return EncryptedFloat64(
            cipher, context, is_fresh, noise_budget, key_set_override
        )

    def refresh_cipher(self) -> None:
        value = self.decrypt()
        refreshed = EncryptedFloat64.create_from_plain(
            value, self.context, self.key_set_override
        )
        self.replace_pointer(refreshed.release())
        self.noise_budget = refreshed.noise_budget
        self.is_fresh = True

    def decrypt(self) -> Union[float, int]:
        return self.rust_library.get().decrypt_float(
            self.context.get_inner_context(),
            self.context.get_private_key(self.key_set_override),
            self.get(),
        )

    def shape(self):
        return [1, 1]

    def __rmul__(
        self, other: Union["EncryptedFloat64", "EncryptedFloatArray", int, float, list]
    ) -> Union["EncryptedFloat64", "EncryptedFloatArray"]:
        return self.__mul__(other)

    def __mul__(
        self, other: Union["EncryptedFloat64", "EncryptedFloatArray", int, float, list]
    ) -> Union["EncryptedFloat64", "EncryptedFloatArray"]:
        if (
            isinstance(other, EncryptedFloat64)
            and EncryptedFloat64.__check_if_zero__(other)
            or EncryptedFloat64.__check_if_zero__(self)
        ):
            return EncryptedFloatZero(self.context, self.key_set_override)

        if isinstance(other, EncryptedFloat64):
            (noise, result) = self.context.execute_function(
                "product_with_cipher",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        if isinstance(other, int):
            other = float(other)

        if isinstance(other, float):
            other = Encrypted.fix_zero_in_plain(other)
            (noise, result) = self.context.execute_function(
                "product_with_plain",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        #        from .encryptedfloatinternalarray import EncryptedFloatInternalArray
        #
        #        if isinstance(other, EncryptedFloatInternalArray):
        #            (noise, result) = self.context.execute_function(
        #                "vector_scale_with_cipher",
        #                self.context.get_inner_context(),
        #                self.context.get_public_key(self.key_set_override),
        #                other,
        #                self,
        #            )
        #
        #            return EncryptedFloatInternalArray.create_from_encrypted_vector_pointer(
        #                result, self.context, False, noise, self.key_set_override
        #            )

        from .encryptedfloatarray import EncryptedFloatArray

        if isinstance(other, EncryptedFloatArray):
            return other * self

        if isinstance(other, list):

            def execute(data: int) -> "EncryptedFloat64":
                return other[data] * self

            interim_result = SunscreenPool.get_instance().map(
                execute, range(0, len(other))
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        raise Exception(
            "Multiplication is not supported for anything other than floats or encrypted floats. But we got "
            + str(other)
        )

    def __div__(self, _):
        raise Exception("Division is unsupported")

    def __rdiv__(self, _):
        raise Exception("Division is unsupported")

    def __rsub__(
        self, other: Union[int, float, "EncryptedFloat64"]
    ) -> "EncryptedFloat64":
        if isinstance(other, EncryptedFloat64):
            (noise, result) = self.context.execute_function(
                "difference_with_cipher",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        if isinstance(other, int):
            other = float(other)

        if isinstance(other, float):
            (noise, result) = self.context.execute_function(
                "difference_with_plain_reverse",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        raise Exception(
            "Subtraction is not supported for anything other than floats or encrypted floats"
        )

    def __sub__(
        self, other: Union[int, float, "EncryptedFloat64"]
    ) -> "EncryptedFloat64":
        if isinstance(other, EncryptedFloat64) and EncryptedFloat64.__check_if_zero__(
            other
        ):
            return self

        if isinstance(other, EncryptedFloat64):
            (noise, result) = self.context.execute_function(
                "difference_with_cipher",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        if isinstance(other, int):
            other = float(other)

        if isinstance(other, float):
            (noise, result) = self.context.execute_function(
                "difference_with_plain",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        raise Exception(
            "Subtraction is not supported for anything other than floats or encrypted floats"
        )

    def __radd__(
        self, other: Union[int, float, "EncryptedFloat64"]
    ) -> "EncryptedFloat64":
        return self.__add__(other)

    def __add__(
        self, other: Union[int, float, "EncryptedFloat64"]
    ) -> "EncryptedFloat64":
        if isinstance(other, EncryptedFloat64) and EncryptedFloat64.__check_if_zero__(
            other
        ):
            return self

        if isinstance(other, EncryptedFloat64):
            (noise, result) = self.context.execute_function(
                "sum_with_cipher",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        if isinstance(other, int):
            other = float(other)

        if isinstance(other, float):
            (noise, result) = self.context.execute_function(
                "sum_with_plain",
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                self,
                other,
            )

            return EncryptedFloat64.create_from_encrypted_cipher_pointer(
                result, self.context, False, noise, self.key_set_override
            )

        raise Exception(
            "Addition is not supported for anything other than floats or encrypted floats "
            + str(type(other))
        )

    @classmethod
    def __check_if_zero__(cls, value: "EncryptedFloat64") -> bool:
        if isinstance(value, EncryptedFloatZero) or (
            (isinstance(value, float) or isinstance(value, int)) and float(value) == 0.0
        ):
            return True
        return False


class EncryptedFloatZero(EncryptedFloat64):
    def __init__(
        self, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ):
        EncryptedFloat64.__init__(
            self,
            None,
            context,
            True,
            EncryptedFloat64.standard_noise_for_fresh_cipher,
            key_set_override,
        )
        if EncryptedFloat64.standard_noise_for_fresh_cipher is None:
            self.pointer = self.rust_library.get().encrypt_float(
                self.context.get_inner_context(),
                self.context.get_public_key(self.key_set_override),
                0,
            )
            EncryptedFloat64.standard_noise_for_fresh_cipher = (
                Encrypted.get_noise_budget_from_runtime(
                    context, self.pointer, key_set_override
                )
            )
            self.noise_budget = EncryptedFloat64.standard_noise_for_fresh_cipher

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            if not self.pointer:
                self.pointer = self.rust_library.get().encrypt_float(
                    self.context.get_inner_context(),
                    self.context.get_public_key(self.key_set_override),
                    0,
                )

            return self.pointer
