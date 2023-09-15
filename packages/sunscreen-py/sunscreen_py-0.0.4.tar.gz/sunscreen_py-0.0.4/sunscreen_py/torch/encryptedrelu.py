import torch
from .encryptedtensor import EncryptedTensor
from ..base.encryptedfloatarray import EncryptedFloatArray


class EncryptedReLU(torch.nn.ReLU):  # type: ignore
    def __init__(self, in_place=False, poly_approx_degree=1):
        super().__init__(in_place)
        self.poly_approx_degree = poly_approx_degree
        if poly_approx_degree < 1 or poly_approx_degree > 2:
            raise Exception("Polynomial Approximation degree only supports 1 or 2")

    def forward(self, input):
        if isinstance(input, EncryptedTensor):
            # We use the polynomial approximation of degree 2
            # relu(x) = 0.47 + 0.50 * x + 0.09 * x^2
            # It is reasonable in the range [-4, 4]
            # A simpler approximation is 0.47 + 0.70x reasonable in
            # range [-1, 2]
            data = EncryptedTensor.__parse_data__(input)
            if isinstance(data, EncryptedFloatArray):
                if self.poly_approx_degree == 2:
                    result = EncryptedTensor(0.47 + (0.50 + 0.09 * data) * data)
                else:
                    result = EncryptedTensor(0.47 + 0.70 * data)
                if self.inplace:
                    input.data = result.data
                    return input
                return result
            else:
                raise Exception("Input was expected to be encrypted")

        return super().forward(input)
