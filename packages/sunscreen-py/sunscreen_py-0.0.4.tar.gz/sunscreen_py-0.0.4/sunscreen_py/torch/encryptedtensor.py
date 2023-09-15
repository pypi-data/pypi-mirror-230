import torch
from ..base.encryptedfloatarray import EncryptedFloatArray
from ..base.context import SunscreenFHEContext, KeySet
from typing import Optional, Sequence, Union

HANDLED_FUNCTIONS = {}

import functools


def implements(torch_function):
    """Register a torch function override for ScalarTensor"""

    def decorator(func):
        functools.update_wrapper(func, torch_function)
        HANDLED_FUNCTIONS[torch_function] = func
        return func

    return decorator


@implements(torch.mul) # type: ignore
def mul(input1, input2):
    input1 = EncryptedTensor.__parse_data__(input1)
    input2 = EncryptedTensor.__parse_data__(input2)
    return EncryptedTensor(input1 * input2) # type: ignore


@implements(torch.add) # type: ignore
def add(input1, input2):
    input1 = EncryptedTensor.__parse_data__(input1)
    input2 = EncryptedTensor.__parse_data__(input2)
    return EncryptedTensor(input1 + input2) # type: ignore


@implements(torch.sub) # type: ignore
def sub(input1, input2):
    input1 = EncryptedTensor.__parse_data__(input1)
    input2 = EncryptedTensor.__parse_data__(input2)
    return EncryptedTensor(input1 - input2) # type: ignore


class EncryptedTensor:
    def __init__(self, held_data: EncryptedFloatArray):
        self.data = held_data

    def decrypt(self):
        return self.data.decrypt()

    def shape(self):
        return self.data.shape()

    def get_context(self) -> SunscreenFHEContext:
        return self.data.context

    def get_key_set_override(self) -> Optional[KeySet]:
        return self.data.key_set_override

    def get_raw(self) -> EncryptedFloatArray:
        return self.data

    @classmethod
    def zeros(cls, dimension, context, key_set_override=None) -> "EncryptedTensor":
        return EncryptedTensor(
            EncryptedFloatArray.create_zeros_for_dimension(
                dimension, context, key_set_override
            )
        )

    @classmethod
    def __parse_data__(cls, data) -> Union[EncryptedFloatArray, Sequence[int], Sequence[float]]:
        if isinstance(data, EncryptedTensor):
            return data.data

        if isinstance(data, torch.Tensor): # type: ignore
            return data.tolist()

        if isinstance(data, list):
            return data

        raise Exception("Unable to parse data")

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        if func not in HANDLED_FUNCTIONS or not all(
            issubclass(t, (torch.Tensor, EncryptedTensor)) for t in types # type: ignore
        ):
            args = [a.tensor() if hasattr(a, "tensor") else a for a in args]
            return NotImplemented
        return HANDLED_FUNCTIONS[func](*args, **kwargs)
