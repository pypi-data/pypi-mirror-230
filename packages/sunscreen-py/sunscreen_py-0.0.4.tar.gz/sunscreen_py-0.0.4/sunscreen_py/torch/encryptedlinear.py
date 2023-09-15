import torch
from .encryptedtensor import EncryptedTensor
from ..base.encryptedfloatarray import EncryptedFloatArray


class EncryptedLinear(torch.nn.Linear):  # type: ignore
    def __init__(self, input_features, output_features, bias=True):
        super().__init__(input_features, output_features, bias)
        self.weight_transpose = None

    def forward(self, input):
        if (
            isinstance(input, EncryptedTensor)
            or isinstance(self.weight, EncryptedTensor)
            or isinstance(self.bias, EncryptedTensor)
        ):
            if not self.weight_transpose:
                self.__transpose__()

            input1 = EncryptedTensor.__parse_data__(input)
            weight = EncryptedTensor.__parse_data__(self.weight_transpose)
            bias = EncryptedTensor.__parse_data__(self.bias)

            if isinstance(input1, EncryptedFloatArray):
                return EncryptedTensor(input1.mm(weight) + bias)
            else:
                raise Exception("Input was expected to be encrypted")

        result = super().forward(input)
        return result

    def __transpose__(self):
        if isinstance(self.weight, EncryptedTensor):
            self.weight_transpose = EncryptedTensor(self.weight.get_raw().transpose())
        elif isinstance(self.weight, torch.Tensor):  # type: ignore
            self.weight_transpose = [
                [0.0 for _ in range(self.weight.shape[0])]
                for _ in range(self.weight.shape[1])
            ]
            for i in range(self.weight.shape[0]):
                for j in range(self.weight.shape[1]):
                    self.weight_transpose[j][i] = self.weight[i][j].tolist()
        else:
            raise Exception("Not implemented")
