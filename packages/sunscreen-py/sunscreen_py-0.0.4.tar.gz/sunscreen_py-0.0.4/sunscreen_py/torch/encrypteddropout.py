import torch
from .encryptedtensor import EncryptedTensor


class EncryptedDropout(torch.nn.Dropout):  # type: ignore
    def __init__(self, p, in_place=False):
        super().__init__(p, in_place)

    def forward(self, input):
        if isinstance(input, EncryptedTensor):
            return input

        return super().forward(input)
