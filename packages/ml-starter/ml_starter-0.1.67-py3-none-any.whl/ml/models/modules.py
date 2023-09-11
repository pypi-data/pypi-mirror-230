"""Miscellaneous shared modules which can be used in various models."""


import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.autograd.function import Function, FunctionCtx
from torch.nn.common_types import _size_1_t

from ml.models.activations import ActivationType, get_activation
from ml.models.norms import NormType, get_norm_1d


class _InvertGrad(Function):
    @staticmethod
    def forward(ctx: FunctionCtx, input: Tensor, scale: float) -> Tensor:  # type: ignore[override]
        ctx.scale = scale
        return input

    @staticmethod
    def backward(ctx: FunctionCtx, grad_output: Tensor) -> tuple[Tensor, None]:  # type: ignore[override]
        return grad_output * ctx.scale, None


def scale_grad(x: Tensor, scale: float) -> Tensor:
    """Scales the gradient of the input.

    Args:
        x: Input tensor.
        scale: Scale factor.

    Returns:
        The identity of the input tensor in the forward pass, and the scaled
        gradient in the backward pass.
    """
    return _InvertGrad.apply(x, scale)


def invert_grad(x: Tensor) -> Tensor:
    return scale_grad(x, -1.0)


class _SwapGrads(Function):
    @staticmethod
    def forward(ctx: FunctionCtx, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:  # type: ignore[override]
        return x, y

    @staticmethod
    def backward(ctx: FunctionCtx, grad_x: Tensor, grad_y: Tensor) -> tuple[Tensor, Tensor]:  # type: ignore[override]
        return grad_y, grad_x


def swap_grads(x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
    """Swaps the gradients of the inputs.

    On the forward pass, this function returns the identity of the inputs.
    On the backward pass, the gradients of X and Y are swapped.

    Args:
        x: First input tensor.
        y: Second input tensor.

    Returns:
        The identity of the inputs in the forward pass, and the swapped
        gradients in the backward pass.
    """
    return _SwapGrads.apply(x, y)


class _CombineGrads(Function):
    @staticmethod
    def forward(ctx: FunctionCtx, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:  # type: ignore[override]
        return x, y

    @staticmethod
    def backward(ctx: FunctionCtx, grad_x: Tensor, grad_y: Tensor) -> tuple[Tensor, Tensor]:  # type: ignore[override]
        grad = grad_x + grad_y
        return grad, grad


def combine_grads(x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
    """Combines the gradients of the inputs.

    On the forward pass, this function returns the identity of the inputs.
    On the backward pass, the gradients of X and Y are summed.

    Args:
        x: First input tensor.
        y: Second input tensor.

    Returns:
        The identity of the inputs in the forward pass, and the summed
        gradients in the backward pass.
    """
    return _CombineGrads.apply(x, y)


def streaming_conv_1d(
    x: Tensor,
    state: tuple[Tensor, int] | None,
    weight: Tensor,
    bias: Tensor | None,
    stride: int,
    padding: int,
    dilation: int,
    groups: int,
) -> tuple[Tensor, tuple[Tensor, int]]:
    """Applies a streaming convolution.

    Args:
        x: The input to the convolution.
        state: The state of the convolution, which is the part of the previous
            input which is left over for computing the current convolution,
            along with an integer tracker for the number of samples to clip
            from the current input.
        weight: The convolution weights.
        bias: The convolution bias.
        stride: The convolution stride.
        padding: The convolution padding.
        dilation: The convolution dilation.
        groups: The convolution groups.

    Returns:
        The output of the convolution, plus the new state tracker.
    """
    if state is None:
        pre_t = 0
        if padding > 0:
            x = torch.cat((x.new_zeros(x.shape[:-1] + (padding,)), x), dim=-1)
    else:
        pre_x, pre_t = state
        x = torch.cat((pre_x, x), dim=-1)
        if pre_t > 0:
            pre_t, x = pre_t - x.shape[-1], x[..., pre_t:]
    (bsz, _, tsz), (chsz_out, _, ksize) = x.shape, weight.shape
    min_tsz = 1 + (ksize - 1) * dilation
    if tsz < min_tsz:
        return x.new_zeros(bsz, chsz_out, 0), (x, pre_t)
    y = F.conv1d(x, weight, bias, stride, 0, dilation, groups)
    t = stride * y.shape[-1]
    return y, (x[:, :, t:], max(0, t - tsz))


def streaming_conv_transpose_1d(
    x: Tensor,
    state: tuple[Tensor, int] | None,
    weight: Tensor,
    bias: Tensor | None,
    stride: int,
    dilation: int,
    groups: int,
) -> tuple[Tensor, tuple[Tensor, int]]:
    """Applies a streaming transposed convolution.

    Args:
        x: The input to the convolution.
        state: The state of the convolution, which is the part of the previous
            input which is left over for computing the current convolution,
            along with an integer tracker for the number of samples to clip
            from the current input.
        weight: The convolution weights.
        bias: The convolution bias.
        stride: The convolution stride.
        dilation: The convolution dilation.
        groups: The convolution groups.

    Returns:
        The output of the convolution, plus the new state tracker.
    """
    y = F.conv_transpose1d(x, weight, bias, stride, 0, 0, groups, dilation)
    bsz, chsz_out, tsz = y.shape
    t = stride * x.shape[-1]
    if state is not None:
        post_y, post_t = state
        if post_t > 0:
            init_y = y.new_zeros(bsz, chsz_out, post_t)
            if bias is not None:
                init_y += bias[..., None]
            y = torch.cat([init_y, y], dim=-1)
        n = min(post_y.shape[-1], y.shape[-1])
        init_y = post_y[..., :n] + y[..., :n]
        if bias is not None:
            init_y -= bias[..., None]
        y = torch.cat((init_y, post_y[..., n:], y[..., n:]), dim=-1)
    return y[..., :t], (y[..., t:], max(0, t - tsz))


class StreamingConv1d(nn.Conv1d):
    """Defines a streaming 1D convolution layer.

    This is analogous to streaming RNNs, where a state is maintained going
    forward in time. For convolutions, the state is simply the part of the
    previous input which is left over for computing the current convolution,
    along with an integer tracker for the number of samples to clip from the
    current input.

    Note that this is a drop-in replacement for ``nn.Conv1d`` so far as the
    weights and biases go, but the forward pass takes an additional state
    argument and returns an additional state output.
    """

    padding: tuple[int, ...]

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_1_t,
        stride: _size_1_t = 1,
        padding: _size_1_t = 0,
        dilation: _size_1_t = 1,
        groups: int = 1,
        bias: bool = True,
    ) -> None:
        super().__init__(
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            in_channels=in_channels,
            out_channels=out_channels,
        )

        assert isinstance(self.padding, tuple) and len(self.padding) == 1 and isinstance(self.padding[0], int)

    def forward(  # type: ignore[override]
        self,
        x: Tensor,
        state: tuple[Tensor, int] | None = None,
    ) -> tuple[Tensor, tuple[Tensor, int]]:
        weight, bias = self.weight, self.bias
        stride, padding, dilation, groups = self.stride[0], self.padding[0], self.dilation[0], self.groups
        return streaming_conv_1d(x, state, weight, bias, stride, padding, dilation, groups)


class StreamingConvTranspose1d(nn.ConvTranspose1d):
    """Defines a streaming 1D transposed convolution layer.

    This is the inverse of ``StreamingConv1d``, with the caveat that padding
    is not supported.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_1_t,
        stride: _size_1_t = 1,
        dilation: _size_1_t = 1,
        groups: int = 1,
        bias: bool = True,
    ) -> None:
        super().__init__(
            kernel_size=kernel_size,
            stride=stride,
            padding=0,
            dilation=dilation,
            groups=groups,
            bias=bias,
            in_channels=in_channels,
            out_channels=out_channels,
        )

    def forward(  # type: ignore[override]
        self,
        x: Tensor,
        state: tuple[Tensor, int] | None = None,
    ) -> tuple[Tensor, tuple[Tensor, int]]:
        weight, bias = self.weight, self.bias
        stride, dilation, groups = self.stride[0], self.dilation[0], self.groups
        return streaming_conv_transpose_1d(x, state, weight, bias, stride, dilation, groups)


def streaming_add(
    a: Tensor,
    b: Tensor,
    state: tuple[Tensor, Tensor] | None = None,
) -> tuple[Tensor, tuple[Tensor, Tensor]]:
    """Performs streaming addition of two tensors.

    Args:
        a: The first tensor, with shape ``(B, C, T)``
        b: The second tensor, with shape ``(B, C, T)``
        state: The state of the addition, which is the leftover part from the
            previous addition.

    Returns:
        The sum of the two tensors, plus the new state.
    """
    if state is not None:
        prev_a, prev_b = state
        a = torch.cat((prev_a, a), dim=-1)
        b = torch.cat((prev_b, b), dim=-1)
    n = min(a.shape[-1], b.shape[-1])
    y = a[..., :n] + b[..., :n]
    return y, (a[..., n:], b[..., n:])


def streamable_cbr(
    in_channels: int,
    out_channels: int,
    kernel_size: int,
    dilation: int,
    norm: NormType = "batch_affine",
    act: ActivationType = "gelu",
    bias: bool = False,
    groups: int = 1,
    group_norm_groups: int | None = None,
) -> nn.Module:
    """Defines a streamable convolution-batchnorm-ReLU module.

    This is a convenience function for defining a streamable convolution
    module. We pad the left side of the input so that each timestep only
    depends on previous timesteps, and not future timesteps, allowing us to
    compute the output of the convolution without having to wait for future
    timesteps.

    Args:
        in_channels: The number of input channels.
        out_channels: The number of output channels.
        kernel_size: The kernel size.
        dilation: The dilation.
        norm: The normalization type.
        act: The activation type.
        bias: Whether to use a bias. This should be turned off if the
            convolution is followed by a batch normalization layer.
        groups: The number of groups for convolution.
        group_norm_groups: The number of groups for group normalization.

    Returns:
        The streamable convolution module.
    """
    pad_amount = (kernel_size - 1) * dilation
    return nn.Sequential(
        nn.ConstantPad1d((pad_amount, 0), 0.0) if pad_amount > 0 else nn.Identity(),
        nn.Conv1d(in_channels, out_channels, kernel_size, groups=groups, dilation=dilation, bias=bias),
        get_norm_1d(norm, dim=out_channels, groups=group_norm_groups),
        get_activation(act, inplace=True),
    )


class residual(nn.Module):  # noqa: N801
    """Defines a residual connection module.

    The child module should take a single tensor as input and return a single
    tensor as output, with the same shape as the input.

    Parameters:
        module: The child module.

    Inputs:
        x: The input tensor, with shape ``(*)``

    Outputs:
        The output tensor, with shape ``(*)``
    """

    def __init__(self, module: nn.Module) -> None:
        super().__init__()

        self.module = module

    def forward(self, x: Tensor) -> Tensor:
        return x + self.module(x)
