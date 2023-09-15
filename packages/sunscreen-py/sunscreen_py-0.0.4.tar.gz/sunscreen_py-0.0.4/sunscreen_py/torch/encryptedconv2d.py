import torch
from .encryptedtensor import EncryptedTensor
from time import time


class EncryptedConv2d(torch.nn.Conv2d): # type: ignore
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size,
        stride=1,
        padding=0,
        bias=True,
    ):
        super().__init__(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            dilation=1,
            groups=1,
            bias=bias,
        )

    def __conv_forward(self, input):
        # Gather Shapes of Kernel + Image + Padding
        xKernShape = self.kernel_size[0]
        yKernShape = self.kernel_size[1]
        input_shape = input.shape()

        # Shape of Output Convolution
        xOutput = int(
            ((input_shape[1] - xKernShape + 2 * self.padding[0]) / self.stride[0]) + 1
        )
        yOutput = int(
            ((input_shape[2] - yKernShape + 2 * self.padding[1]) / self.stride[1]) + 1
        )
        output = EncryptedTensor.zeros(
            [self.out_channels, xOutput, yOutput],
            input.get_context(),
            input.get_key_set_override(),
        ).get_raw()

        # Apply Equal Padding to All Sides
        if self.padding != 0:
            imagePadded = EncryptedTensor.zeros(
                [
                    input_shape[0],
                    input_shape[1] + self.padding[0] * 2,
                    input_shape[2] + self.padding[1] * 2,
                ],
                input.get_context(),
                input.get_key_set_override(),
            ).get_raw()
            for i in range(0, input_shape[0]):
                start_x = int(self.padding[0])
                end_x = start_x + input_shape[1]
                for j in range(start_x, end_x):
                    start_y = int(self.padding[1])
                    end_y = start_y + input_shape[2]
                    for k in range(start_y, end_y):
                        imagePadded[i][j][k] = input.get_raw()[i][j - start_x][
                            k - start_y
                        ]
        else:
            imagePadded = input.get_raw()

        weights = self.weight.tolist()
        bias = self.bias.tolist()

        def __inner_convolve__(data):
            nonlocal output
            (out_chan, x, y) = data
            channel_sum = 0
            for in_chan in range(self.in_channels):
                channel_sum = (
                    channel_sum
                    + (
                        imagePadded[
                            in_chan,
                            x : x + xKernShape,
                            y : y + yKernShape,
                        ]
                        * weights[out_chan][in_chan]
                    ).sum()
                )
            output[out_chan][x][y] = bias[out_chan] + channel_sum

        # Iterate through image and create convolution points
        convolution_points = []
        for y in range(input_shape[2]):
            # Exit Convolution
            if y > input_shape[2] - yKernShape:
                break
            # Only Convolve if y has gone down by the specified Strides
            if y % self.stride[1] == 0:
                for x in range(input_shape[1]):
                    # Go to next row once kernel is out of bounds
                    if x > input_shape[1] - xKernShape:
                        break
                    # Only Convolve if x has moved by the specified Strides
                    if x % self.stride[0] == 0:
                        for out_chan in range(self.out_channels):
                            convolution_points.append((out_chan, x, y))

        start_time = time()
        for i in range(0, len(convolution_points)):
            __inner_convolve__(convolution_points[i])
            if i % 20 == 0:
                print(
                    str(i)
                    + " took an average of "
                    + str((time() - start_time) / (i + 1))
                )
        #        with ThreadPool(1) as pool:
        #            pool.map(__inner_convolve__, convolution_points)

        print("Done convolution")
        return EncryptedTensor(output)

    def forward(self, input):
        if isinstance(input, EncryptedTensor):
            return self.__conv_forward(input)

        return super().forward(input)
