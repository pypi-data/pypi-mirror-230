import ctypes
from .buffer import SunscreenBuffer, DEFAULT_BUFFER_LENGTH
from .rustlibrary import RustLibrary
from typing import Optional, cast
from enum import IntFlag
from ..internal.sunscreenpool import SunscreenPool


class OperationsSupported(IntFlag):
    NoOperation = 0
    CipherPlainSum = 1 << 0
    CipherCipherSum = 1 << 1
    CipherPlainDifference = 1 << 2
    PlainCipherDifference = 1 << 3
    CipherCipherDifference = 1 << 4
    CipherPlainProduct = 1 << 5
    CipherCipherProduct = 1 << 6


#    VectorCipherPlainDotProduct = 1 << 7
#    VectorCipherCipherDotProduct = 1 << 8
#    VectorCipherPlainSum = 1 << 9
#    VectorCipherCipherSum = 1 << 10
#    VectorCipherPlainScale = 1 << 11
#    VectorCipherCipherScale = 1 << 12
#    VectorPlainCipherScale = 1 << 13
#    VectorCipherPlainDifference = 1 << 14
#    VectorPlainCipherDifference = 1 << 15
#    VectorCipherCipherDifference = 1 << 16
#    VectorCipherCipherProduct = 1 << 17
#    VectorCipherPlainProduct = 1 << 18
#    MLLogisticRegressionTraining = 1 << 19
#    MLLogisticRegressionInference = 1 << 20


class KeySet:
    def __init__(
        self,
        public_key: ctypes.c_void_p,
        private_key: Optional[ctypes.c_void_p],
        rust_library: RustLibrary,
    ):
        self.public_key = public_key
        self.private_key = private_key
        self.rust_library = rust_library

    @classmethod
    def initialize_from_pointers(
        cls, public_key: ctypes.c_void_p, private_key: Optional[ctypes.c_void_p] = None
    ) -> "KeySet":
        return KeySet(public_key, private_key, RustLibrary())

    @classmethod
    def initialize_from_buffers(
        cls, public_key: SunscreenBuffer, private_key: Optional[SunscreenBuffer] = None
    ) -> "KeySet":
        library = RustLibrary()
        public_key_obj = library.get().get_public_key_from_string(public_key.get())
        private_key_obj = None
        if private_key:
            raise Exception("Unimplemented with private key")
            private_key_obj = library.get().get_private_key_from_string(
                private_key.get()
            )

        return KeySet(public_key_obj, private_key_obj, library)

    def get_public_key(self) -> ctypes.c_void_p:
        return self.public_key

    def get_private_key(self) -> Optional[ctypes.c_void_p]:
        return self.private_key

    def get_public_key_as_object(self) -> SunscreenBuffer:
        param_buffer = SunscreenBuffer.create_for_length(DEFAULT_BUFFER_LENGTH)

        self.rust_library.get().get_public_key_as_string(
            self.public_key, param_buffer.get()
        )
        return param_buffer

    def __del__(self):
        if self.public_key:
            self.rust_library.get().release_public_key(self.public_key)
        if self.private_key:
            self.rust_library.get().release_private_key(self.private_key)


class SunscreenFHEContext:
    def __init__(
        self,
        rust_library: RustLibrary,
        context: ctypes.c_void_p,
        is_refresh_enabled: bool = False,
    ) -> None:
        self.rust_library: RustLibrary = rust_library
        self.context: ctypes.c_void_p = context
        self.function_noise_budgets: dict[str, int] = {}
        self.functions_use_count: dict[str, int] = {}
        self.key_set: Optional[KeySet] = None
        self.thread_count: int = 100
        self.is_refresh_enabled: bool = is_refresh_enabled
        SunscreenPool.initialize(self.thread_count)

    @classmethod
    def create_from_params(
        cls, params: SunscreenBuffer, is_refresh_enabled: bool = False
    ) -> "SunscreenFHEContext":
        rust_library = RustLibrary()
        context = rust_library.get().initialize_context_with_params_as_string(
            params.get()
        )
        return SunscreenFHEContext(rust_library, context, is_refresh_enabled)

    @classmethod
    def create_from_standard_params(
        cls, is_refresh_enabled: bool = False
    ) -> "SunscreenFHEContext":
        rust_library = RustLibrary()
        context = rust_library.get().initialize_context_with_standard_params()
        return SunscreenFHEContext(rust_library, context, is_refresh_enabled)

    def __del__(self):
        if self.context:
            self.rust_library.get().release_context(self.context)

    def get_rust_library(self) -> RustLibrary:
        return self.rust_library

    def get_inner_context(self) -> ctypes.c_void_p:
        return self.context

    @classmethod
    def create_for_supported_operations(
        cls,
        operations: int,
        enable_chaining: bool = True,
        is_refresh_enabled: bool = False,
    ) -> "SunscreenFHEContext":
        rust_library = RustLibrary()
        context = rust_library.get().initialize_context(operations, enable_chaining)
        return SunscreenFHEContext(rust_library, context, is_refresh_enabled)

    def get_params(self) -> SunscreenBuffer:
        param_buffer = SunscreenBuffer.create_for_length(DEFAULT_BUFFER_LENGTH)
        self.rust_library.get().get_params_as_string(self.context, param_buffer.get())

        return param_buffer

    def get_public_key(
        self, key_set_override: Optional[KeySet] = None
    ) -> Optional[ctypes.c_void_p]:
        if key_set_override:
            return key_set_override.get_public_key()

        if self.key_set:
            return self.key_set.get_public_key()

        return None

    def get_private_key(
        self, key_set_override: Optional[KeySet] = None
    ) -> Optional[ctypes.c_void_p]:
        if key_set_override:
            return key_set_override.get_private_key()

        if self.key_set:
            return self.key_set.get_private_key()

        return None

    def generate_keys(self) -> KeySet:
        keys = self.rust_library.get().generate_keys(self.context)
        public_key = self.rust_library.get().get_public_key(keys)
        private_key = self.rust_library.get().get_private_key(keys)
        self.key_set = KeySet(public_key, private_key, self.rust_library)
        return self.key_set

    def is_cipher_refresh_enabled(self) -> bool:
        return self.is_refresh_enabled

    def execute_function(
        self, function_name: str, *args
    ) -> tuple[Optional[int], ctypes.c_void_p]:
        min_noise_needed_after_operation: int = 16
        min_noise_in_ciphers: int = 2048
        fn_noise_needed: Optional[int] = self.get_noise_budget_for_function(
            function_name
        )
        fn_noise_needed: Optional[int] = (
            None
            if self.should_noise_budget_be_updated(function_name)
            else fn_noise_needed
        )

        arg_list = list(args)
        key_set_override: Optional[KeySet] = None

        from .encrypted import Encrypted

        for idx, arg in enumerate(arg_list):
            if self.is_cipher_refresh_enabled() and isinstance(arg, Encrypted):
                arg_encrypted = cast(Encrypted, arg)
                if arg_encrypted.noise_budget is not None:
                    if not arg_encrypted.is_fresh and (
                        fn_noise_needed is None
                        or fn_noise_needed
                        >= (
                            arg_encrypted.noise_budget
                            + min_noise_needed_after_operation
                        )
                    ):
                        # Re-encrypt the cipher
                        key_set_override = arg_encrypted.key_set_override
                        arg_encrypted.refresh_cipher()
                        if min_noise_in_ciphers > arg_encrypted.noise_budget:
                            min_noise_in_ciphers = arg_encrypted.noise_budget
                    elif min_noise_in_ciphers > arg_encrypted.noise_budget:
                        min_noise_in_ciphers = arg_encrypted.noise_budget

        for idx, arg in enumerate(arg_list):
            if isinstance(arg, Encrypted) or isinstance(arg, SunscreenBuffer):
                arg_list[idx] = arg.get()

        f = getattr(self.get_rust_library().get(), function_name)
        updated_args = tuple(arg_list)
        result = f(*updated_args)

        noise_budget_in_answer = None
        if fn_noise_needed is None and f.restype == ctypes.c_void_p:
            noise_budget_in_answer = Encrypted.get_noise_budget_from_runtime(
                self, result, key_set_override
            )
            if noise_budget_in_answer is not None:
                noise_needed = min_noise_in_ciphers - noise_budget_in_answer
                self.update_noise_budget_for_function(function_name, noise_needed)
        elif fn_noise_needed is not None:
            noise_budget_in_answer = min_noise_in_ciphers - fn_noise_needed

        self.record_function_noise_use(function_name)
        return (noise_budget_in_answer, result)

    def get_noise_budget_for_function(self, function_name: str) -> Optional[int]:
        if function_name in self.function_noise_budgets:
            return self.function_noise_budgets[function_name]

        return None

    def update_noise_budget_for_function(self, function_name: str, budget: int) -> None:
        if function_name in self.function_noise_budgets:
            if self.function_noise_budgets[function_name] < budget:
                self.function_noise_budgets[function_name] = budget
        else:
            self.function_noise_budgets[function_name] = budget

    def record_function_noise_use(self, function_name: str) -> None:
        if function_name in self.functions_use_count:
            self.functions_use_count[function_name] += 1
        else:
            self.functions_use_count[function_name] = 1

    def should_noise_budget_be_updated(self, function_name: str) -> bool:
        if function_name in self.functions_use_count:
            usage: int = self.functions_use_count[function_name]
            return usage % 6 == 0  # (usage & (usage - 1) == 0) and usage != 0
        else:
            return True
