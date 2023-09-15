import torch
import math
from .encryptedtensor import EncryptedTensor
from ..base.encryptedfloatarray import EncryptedFloatArray

class EncryptedTanh(torch.nn.Tanh): # type: ignore
    def __init__(self, poly_approx_degree=1):
        super().__init__()
        self.poly_approx_degree = poly_approx_degree
        if poly_approx_degree < 1 or poly_approx_degree > 2:
            raise Exception("Polynomial Approximation degree only supports 1 or 2")

    def forward(self, input):
        if isinstance(input, EncryptedTensor):
            # We use the polynomial approximation of degree 2
            # tanh(x) = 2.5e−12 + 0.29 * x − 4.0e−12 * x^2
            data = EncryptedTensor.__parse_data__(input)
            if isinstance(data, EncryptedFloatArray):
                if self.poly_approx_degree == 1:
                    result = EncryptedTensor(2.5 * math.exp(-12) + 0.25 * data)
                else:
                    result = EncryptedTensor(
                        2.5 * math.exp(-12) + (0.29 - 4.0 * math.exp(-12) * data) * data
                    )
                return result
            else:
                raise Exception("Input was expected to be encrypted")

        return super().forward(input)
