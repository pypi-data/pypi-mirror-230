from .encryptedfloat64 import EncryptedFloat64, EncryptedFloatZero
from ..internal.sunscreenpool import SunscreenPool
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from .buffer import SunscreenBuffer
from typing import Optional, Any, Union, Sequence, Callable
import ctypes
from math import ceil


class EncryptedFloatArray(Encrypted):
    InternalType = Union[Sequence[EncryptedFloat64], Sequence["EncryptedFloatArray"]]
    InternalUnitType = Union[EncryptedFloat64, "EncryptedFloatArray"]
    StandardOperandType = Union[
        "EncryptedFloatArray",
        Sequence[int],
        Sequence[float],
        EncryptedFloat64,
        float,
        int,
    ]
    MatrixOperandType = Union["EncryptedFloatArray", Sequence[int], Sequence[float]]
    sub_arrays: InternalType = []

    def __init__(
        self,
        ciphers: InternalType,
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ):
        Encrypted.__init__(
            self, None, context, False, None, key_set_override
        )
        self.sub_arrays = ciphers


    @classmethod
    def create_zeros_for_dimension(
        cls,
        dimension: list[int],
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloatArray":
        if len(dimension) == 0:
            raise Exception("Can't create an array with 0 dimensions")
        if len(dimension) == 1:
            ciphers = [
                EncryptedFloatZero(context, key_set_override)
                for _ in range(0, dimension[0])
            ]
        else:
            ciphers = [
                EncryptedFloatArray.create_zeros_for_dimension(
                    dimension[1:], context, key_set_override
                )
                for _ in range(0, dimension[0])
            ]

        return EncryptedFloatArray(ciphers, context, key_set_override)

    @classmethod
    def create_from_plain_vectors(
        cls,
        vector: Union[list[int], list[float]],
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloatArray":
        if isinstance(vector[0], int):
            vector = [float(i) for i in vector]

        if isinstance(vector[0], float):
            executor = lambda data: EncryptedFloat64.create_from_plain(
                data, context, key_set_override
            )

            ciphers = SunscreenPool.get_instance().map(executor, vector)
        else:
            executor = lambda data: EncryptedFloatArray.create_from_plain_vectors(
                data, context, key_set_override
            )

            ciphers = SunscreenPool.get_instance().map(executor, vector)

        return EncryptedFloatArray(ciphers, context, key_set_override)

    @classmethod
    def create_from_encrypted_cipher(
        cls,
        cipher_array: list,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        noise_budget: Optional[int] = None,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloatArray":
        if isinstance(cipher_array, list):
            if isinstance(cipher_array[0], SunscreenBuffer):
                interim_res: list[EncryptedFloat64] = [
                    EncryptedFloat64.create_from_encrypted_cipher(
                        i, context, is_fresh, noise_budget, key_set_override
                    )
                    for i in cipher_array
                ]
                return EncryptedFloatArray.create_from_encrypted_vector_objects(
                    interim_res, context, is_fresh, key_set_override
                )
            if isinstance(cipher_array[0], list):
                interim_result: list["EncryptedFloatArray"] = [
                    EncryptedFloatArray.create_from_encrypted_cipher(
                        i, context, is_fresh, noise_budget, key_set_override
                    )
                    for i in cipher_array
                ]
                return EncryptedFloatArray.create_from_encrypted_vector_objects(
                    interim_result, context, is_fresh, key_set_override
                )
        raise Exception("Ciphers must be an array")

    @classmethod
    def create_from_encrypted_vector_objects(
        cls,
        ciphers: InternalType,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedFloatArray":
        # if isinstance(ciphers[0], EncryptedFloat):
        #    plain = [i.decrypt() for i in ciphers]
        #    return EncryptedFloatArray.create_from_plain_vectors(
        #        plain, context, key_set_override
        #    )
        # if isinstance(ciphers[0], EncryptedFloatInternalArray) or isinstance(
        #    ciphers[0], EncryptedFloatArray
        # ):
        #    return EncryptedFloatArray(ciphers, context, key_set_override)

        # raise Exception("Unknown type: " + str(type(ciphers[0])))
        return EncryptedFloatArray(ciphers, context, key_set_override)

    def refresh_cipher(self) -> None:
        for sub_element in self.sub_arrays:
            sub_element.refresh_cipher()

    def decrypt(self) -> list[float]:
        return [i.decrypt() for i in self.sub_arrays]

    def __getitem__(self, index: Union[int, Sequence[int], slice]) -> InternalUnitType:
        if isinstance(index, int):
            return self.sub_arrays[index]

        # index is a tuple
        first, rest = index[0], index[1:]
        # Is first an int or a slice
        if isinstance(first, int) and isinstance(
            self.sub_arrays[0], EncryptedFloatArray
        ):
            return self.sub_arrays[first][rest]

        # It is a slice
        start = 0 if first.start == None else first.start
        stop = first.stop if first.stop >= 0 else len(self.sub_arrays) + first.stop
        step = 1 if first.step == None else first.step

        # Collect data
        ciphers_interested = []
        while start < stop and start < len(self.sub_arrays):
            if len(rest) > 0:
                ciphers_interested.append(self.sub_arrays[start][rest])
            else:
                ciphers_interested.append(self.sub_arrays[start])
            start += step

        return EncryptedFloatArray(
            ciphers_interested, self.context, self.key_set_override
        )

    def __setitem__(self, index: int, item: InternalUnitType):
        if not isinstance(index, int):
            raise Exception("Can't handle non int indexing")

        if (
            isinstance(self.sub_arrays[0], EncryptedFloat64)
            and isinstance(item, EncryptedFloat64)
        ) or (
            isinstance(self.sub_arrays[0], EncryptedFloatArray)
            and isinstance(item, EncryptedFloatArray)
        ):
            self.sub_arrays[index] = item  # type: ignore
            return

        raise Exception(
            "New item being set has wrong type: "
            + str(type(item))
            + " while the current one is "
            + str(type(self.sub_arrays[0]))
        )

    def get_cipher(self):
        if len(self.sub_arrays) > 1:
            if isinstance(self.sub_arrays[0], EncryptedFloat64):
                s = [i.get_cipher() for i in self.sub_arrays]
                return sum(s, [])
            if isinstance(self.sub_arrays[0], EncryptedFloatArray):
                return [i.get_cipher() for i in self.sub_arrays]
        else:
            return [self.sub_arrays[0].get_cipher()]

    def shape(self):
        if len(self.sub_arrays) == 0:
            return [0, 0]

        if isinstance(self.sub_arrays[0], EncryptedFloat64):
            return [1, len(self.sub_arrays)]

        if isinstance(self.sub_arrays[0], EncryptedFloatArray):
            # Assuming sub arrays are same/similar
            sub_shape = self.sub_arrays[0].shape()
            if sub_shape[0] == 0:
                raise Exception("Shape of the Float Array is messed up")
            if sub_shape[0] == 1:
                return [len(self.sub_arrays)] + sub_shape[1:]
            return [len(self.sub_arrays)] + sub_shape

        raise Exception("Sub array is an unsupported type ")

    def dot(
        self, other: MatrixOperandType
    ) -> Union["EncryptedFloatArray", EncryptedFloat64]:
        if isinstance(other, EncryptedFloatArray) and isinstance(
            self.sub_arrays[0], EncryptedFloat64
        ):
            if len(other.sub_arrays) != len(self.sub_arrays):
                raise Exception("Unable to do dot product with vectors of uneven size")

            executor: Callable[..., Union["EncryptedFloatArray", EncryptedFloat64]] = (
                lambda data: self.sub_arrays[data] * other.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            result: EncryptedFloatArray.InternalUnitType = EncryptedFloatZero(
                self.context, self.key_set_override
            )
            for x in interim_result:
                result = result + x
            return result

        if isinstance(other, list) and isinstance(other[0], int):
            other = [float(i) for i in other]

        if isinstance(other, list) and isinstance(other[0], float):
            # plain_sub_arrays = EncryptedFloatArray.__chunk(
            #    other, EncryptedFloatInternalArray.STANDARD_LENGTH
            # )

            def execute(data):
                return self.sub_arrays[data] * other[data]

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    execute, range(0, len(self.sub_arrays))
                )
            )

            result: EncryptedFloatArray.InternalUnitType = EncryptedFloatZero(
                self.context, self.key_set_override
            )
            for x in interim_result:
                result = result + x
            return result

        raise Exception("Dot product not supported " + str(type(other[0])))

    def sum(self) -> EncryptedFloat64:
        def execute(data):
            if isinstance(self.sub_arrays[data], EncryptedFloat64):
                return self.sub_arrays[data]

            return self.sub_arrays[data].sum()

        interim_result: Sequence[EncryptedFloat64] = SunscreenPool.get_instance().map(
            execute, range(0, len(self.sub_arrays))
        )

        result: EncryptedFloat64 = EncryptedFloatZero(
            self.context, self.key_set_override
        )
        for x in interim_result:
            result = result + x
        return result

    def transpose(self) -> "EncryptedFloatArray":
        if len(self.shape()) != 2:
            raise Exception(
                "Matrix Multiplication is only implemented for 2 D matrices"
            )

        rows = self.shape()[0]
        cols = self.shape()[1]

        result: "EncryptedFloatArray" = EncryptedFloatArray.create_zeros_for_dimension(
            [cols, rows], self.context, self.key_set_override
        )
        for i in range(rows):
            for j in range(cols):
                result[j][i] = self[i][j]

        return result

    def mm(
        self,
        other: MatrixOperandType,
        vectorize: bool = False,
    ) -> "EncryptedFloatArray":
        if len(self.shape()) != 2:
            raise Exception(
                "Matrix Multiplication is only implemented for 2 D matrices"
            )

        R1: int = self.shape()[0]
        C1: int = self.shape()[1]
        R2: int = (
            other.shape()[0] if isinstance(other, EncryptedFloatArray) else len(other)
        )
        C2: int = (
            other.shape()[1]
            if isinstance(other, EncryptedFloatArray)
            else len(other[0])
        )

        if C1 != R2:
            raise Exception(
                f"Can't perform matrix multiplication for shapes: {R1} X {C1} and {R2} X {C2}"
            )

        if not vectorize:
            if R1 > 1:
                result = EncryptedFloatArray.create_zeros_for_dimension(
                    [R1, C2], self.context, self.key_set_override
                )
            else:
                result = EncryptedFloatArray.create_zeros_for_dimension(
                    [C2], self.context, self.key_set_override
                )

            for i in range(R1):
                for j in range(C2):
                    for k in range(R2):
                        if R1 > 1:
                            result[i][j] = result[i][j] + self[i][k] * other[k][j]
                        else:
                            result[j] = result[j] + self[k] * other[k][j]
        else:
            if R1 == 1:
                if isinstance(other, list):
                    other = EncryptedFloatArray.__list_transpose(other)
                    length = len(other)
                elif isinstance(other, EncryptedFloatArray):
                    other = other.transpose()
                    length = other.shape[0]
                else:
                    raise Exception("Unsupported type")

                result = EncryptedFloatArray(
                    [self.dot(other[i]) for i in range(length)],
                    self.context,
                    self.key_set_override,
                )
            else:
                result = EncryptedFloatArray(
                    [
                        self[i].mm(other, vectorize=vectorize)
                        for i in range(self.shape()[0])
                    ],
                    self.context,
                    self.key_set_override,
                )

        return result

    def __rmul__(self, other: StandardOperandType) -> "EncryptedFloatArray":
        return self.__mul__(other)

    def __mul__(self, other: StandardOperandType) -> "EncryptedFloatArray":
        if isinstance(other, EncryptedFloatArray):
            if len(other.sub_arrays) != len(self.sub_arrays):
                raise Exception(
                    "Unable to do multiplication with vectors of uneven size"
                )

            executor: Callable[..., Union["EncryptedFloatArray", EncryptedFloat64]] = (
                lambda data: other.sub_arrays[data] * self.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        if isinstance(other, list) and isinstance(other[0], list):
            if len(other) != len(self.sub_arrays):
                raise Exception(
                    "Unable to do multiplication with vectors of uneven size"
                )

            executor: Callable[..., Union["EncryptedFloatArray", EncryptedFloat64]] = (
                lambda data: other[data] * self.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        if isinstance(other, list) and isinstance(other[0], float):
            # plain_sub_arrays = EncryptedFloatArray.__chunk(
            #    other, EncryptedFloatInternalArray.STANDARD_LENGTH
            # )

            executor: Callable[..., Union["EncryptedFloatArray", EncryptedFloat64]] = (
                lambda data: other[data] * self.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        if (
            isinstance(other, float)
            or isinstance(other, EncryptedFloat64)
            or isinstance(other, int)
        ):
            executor: Callable[..., Union["EncryptedFloatArray", EncryptedFloat64]] = (
                lambda data: other * self.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        raise Exception(
            "Multiplication is only supported for arrays of floats and encrypted arrays of floats"
        )

    def __radd__(
        self,
        other: StandardOperandType,
    ) -> "EncryptedFloatArray":
        return self.__add__(other)

    def __add__(
        self,
        other: StandardOperandType,
    ) -> "EncryptedFloatArray":
        if isinstance(other, EncryptedFloatArray):
            if len(other.sub_arrays) != len(self.sub_arrays):
                raise Exception("Unable to do dot product with vectors of uneven size")

            executor: Callable[..., EncryptedFloatArray.InternalUnitType] = (
                lambda data: other.sub_arrays[data] + self.sub_arrays[data]
            )

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        if isinstance(other, int):
            other = float(other)

        if isinstance(other, float):
            other = [other]

        if isinstance(other, list) and isinstance(other[0], int):
            other = [float(i) for i in other]

        if isinstance(other, list) and isinstance(other[0], float):
            # plain_sub_arrays = EncryptedFloatArray.__chunk(
            #    other, EncryptedFloatInternalArray.STANDARD_LENGTH
            # )

            if len(other) == 1:
                other = other * len(self.sub_arrays)

            executor = lambda data: other[data] + self.sub_arrays[data]

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    executor, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        raise Exception(
            "Addition is only supported for arrays of floats and encrypted arrays of floats"
            + str(type(other))
        )

    def __div__(self, _):
        raise Exception("Division is unsupported")

    def __rdiv__(self, _):
        raise Exception("Division is unsupported")

    def __rsub__(self, other: Union[float, Sequence[float]]) -> "EncryptedFloatArray":
        if isinstance(other, float):
            other = [other] * len(self.sub_arrays)

        if isinstance(other, list) and isinstance(other[0], float):
            # plain_sub_arrays = EncryptedFloatArray.__chunk(
            #    other, EncryptedFloatInternalArray.STANDARD_LENGTH
            # )

            def execute(data):
                return other[data] - self.sub_arrays[data]

            interim_result: EncryptedFloatArray.InternalType = (
                SunscreenPool.get_instance().map(
                    execute, range(0, len(self.sub_arrays))
                )
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        raise Exception("Reverse subtraction is only supported for arrays of floats")

    def __sub__(self, other: StandardOperandType) -> "EncryptedFloatArray":
        if isinstance(other, EncryptedFloatArray):
            if len(other.sub_arrays) != len(self.sub_arrays):
                raise Exception("Unable to do subtraction with vectors of uneven size")

            def execute(data):
                return self.sub_arrays[data] - other.sub_arrays[data]

            interim_result = SunscreenPool.get_instance().map(
                execute, range(0, len(self.sub_arrays))
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        if isinstance(other, float):
            other = [other] * len(self.sub_arrays)

        if isinstance(other, list) and isinstance(other[0], float):
            # plain_sub_arrays = EncryptedFloatArray.__chunk(
            #    other, EncryptedFloatInternalArray.STANDARD_LENGTH
            # )

            def execute(data):
                return self.sub_arrays[data] - other[data]

            interim_result = SunscreenPool.get_instance().map(
                execute, range(0, len(self.sub_arrays))
            )

            return EncryptedFloatArray.create_from_encrypted_vector_objects(
                interim_result, self.context, False, self.key_set_override
            )

        raise Exception(
            "Subtraction is only supported for arrays of floats and encrypted arrays of floats"
        )

    #    @classmethod
    #    def __chunk(cls, lst, size):
    #        n = ceil(len(lst) / size)
    #        return list(map(lambda x: lst[x * size : x * size + size], list(range(n))))

    @classmethod
    def __list_transpose(cls, lst):
        dim1 = len(lst)
        dim2 = 1
        if isinstance(lst[0], list):
            dim2 = len(lst[0])
        transpose = [[None for _ in range(dim1)] for _ in range(dim2)]
        for i in range(dim1):
            if dim2 > 1:
                for j in range(dim2):
                    transpose[j][i] = lst[i][j]
            else:
                transpose[0][i] = lst[i]
        return transpose
