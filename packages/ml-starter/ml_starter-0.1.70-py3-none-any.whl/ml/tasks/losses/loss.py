"""Defines a general-purpose API for losses.

.. highlight:: python
.. code-block:: python

    from ml.tasks.losses.loss import loss_fn

    mse_loss = loss_fn("mse")
    loss = mse_loss(pred, target)
    assert loss.shape == pred.shape

The following loss functions are supported:

Modality-Agnostic
-----------------

- ``"bce-logits"``: Binary cross-entropy loss with logits
- ``"bce"``: Binary cross-entropy loss
- ``"huber"``: Huber loss, which is a smoothed version of the L1 loss
- ``"l1"``: L1 loss
- ``"log-cosh"``: Log cosh loss, which is a smoothed version of the L1 loss
- ``"mse"``: Mean squared error loss
- ``"xent"``: Cross-entropy loss

Audio
-----

- ``"log-stft-magnitude"``: Log STFT magnitude loss
- ``"mel"``: Mel spectrogram loss
- ``"mfcc"``: Mel-frequency cepstral coefficients loss
- ``"multi-stft"``: Multi-resolution short-time Fourier transform loss
- ``"spectral-convergence"``: Spectral convergence loss
- ``"stft"``: Short-time Fourier transform loss

Image
-----

- ``"image-grad"``: Image gradient loss
- ``"lpips"``: Learned perceptual image patch similarity loss
- ``"ssim"``: Structural similarity index loss

KL Divergence
-------------

- ``"kl-pair"``: KL divergence loss between two Gaussian distributions
- ``"kl-single"``: KL divergence loss between a Gaussian distribution and a standard normal
"""

import functools
from typing import Callable, Literal, overload

import torch
from torch import Tensor, nn

from ml.tasks.losses.audio import (
    MelLoss,
    MFCCLoss,
    MultiResolutionSTFTLoss,
    STFTLoss,
    WindowFn,
    log_stft_magnitude_loss,
    spectral_convergence_loss,
)
from ml.tasks.losses.image import LPIPS, ImageGradLoss, SsimFn, SSIMLoss
from ml.tasks.losses.kl import kl_div_pair_loss, kl_div_single_loss

LossFn = Literal[
    # Modality-agnostic
    "bce-logits",
    "bce",
    "huber",
    "l1",
    "log-cosh",
    "mse",
    "xent",
    # Audio
    "log-stft-magnitude",
    "mel",
    "mfcc",
    "multi-stft",
    "spectral-convergence",
    "stft",
    # Image
    "image-grad",
    "lpips",
    "ssim",
    # KL divergence
    "kl-pair",
    "kl-single",
]

# Defines type aliases for the different loss functions.
OneInOneOutLoss = Callable[[Tensor], Tensor]
TwoInOneOutLoss = Callable[[Tensor, Tensor], Tensor]
TwoInTwoOutLoss = Callable[[Tensor, Tensor], tuple[Tensor, Tensor]]
FourInOneOutLoss = Callable[[Tensor, Tensor, Tensor, Tensor], Tensor]
LossFnSpec = OneInOneOutLoss | TwoInOneOutLoss | TwoInTwoOutLoss | FourInOneOutLoss


def log_cosh_loss(pred: Tensor, target: Tensor) -> Tensor:
    loss = pred - target
    return torch.log(torch.cosh(loss))


@overload
def loss_fn(loss: Literal["mse"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["l1"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["huber"], *, huber_beta: float = 1.0) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["log-cosh"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["xent"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["bce"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["bce-logits"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["spectral-convergence"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(loss: Literal["log-stft-magnitude"]) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["stft"],
    *,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    window_fn: WindowFn = "hann",
) -> TwoInTwoOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["multi-stft"],
    *,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    window_fn: WindowFn = "hann",
    fft_size_multiples: list[float] = [0.5, 1.0, 2.0],
) -> TwoInTwoOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["mel"],
    *,
    sample_rate: int,
    f_min: float = 0.0,
    f_max: float | None = None,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    n_mels: int = 80,
    window_fn: WindowFn = "hann",
) -> TwoInTwoOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["mfcc"],
    *,
    sample_rate: int,
    f_min: float = 0.0,
    f_max: float | None = None,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    n_mels: int = 80,
    n_mfcc: int = 40,
    log_mels: bool = False,
    window_fn: WindowFn = "hann",
) -> TwoInTwoOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["ssim"],
    *,
    image_kernel_size: int = 3,
    ssim_stride: int = 1,
    ssim_channels: int = 3,
    ssim_mode: SsimFn = "avg",
    image_sigma: float = 1.0,
    ssim_dynamic_range: float = 1.0,
) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["image-grad"],
    *,
    image_kernel_size: int = 3,
    image_sigma: float = 1.0,
) -> OneInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["lpips"],
    *,
    pretrained: bool = True,
    requires_grad: bool = False,
) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["kl-single"],
    *,
    clamp_min: float = -30.0,
    clamp_max: float = 20.0,
) -> TwoInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: Literal["kl-pair"],
    *,
    clamp_min: float = -30.0,
    clamp_max: float = 20.0,
) -> FourInOneOutLoss:
    ...


@overload
def loss_fn(
    loss: LossFn,
    *,
    huber_beta: float = 1.0,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    window_fn: WindowFn = "hann",
    fft_size_multiples: list[float] = [0.5, 1.0, 2.0],
    image_kernel_size: int = 3,
    ssim_stride: int = 1,
    ssim_channels: int = 3,
    ssim_mode: SsimFn = "avg",
    image_sigma: float = 1.0,
    ssim_dynamic_range: float = 1.0,
) -> LossFnSpec:
    ...


def loss_fn(
    loss: LossFn,
    *,
    huber_beta: float = 1.0,
    sample_rate: int = 16000,
    f_min: float = 0.0,
    f_max: float | None = None,
    fft_size: int = 1024,
    shift_size: int = 120,
    win_length: int = 600,
    n_mels: int = 80,
    n_mfcc: int = 40,
    log_mels: bool = False,
    window_fn: WindowFn = "hann",
    fft_size_multiples: list[float] = [0.5, 1.0, 2.0],
    image_kernel_size: int = 3,
    ssim_stride: int = 1,
    ssim_channels: int = 3,
    ssim_mode: SsimFn = "avg",
    image_sigma: float = 1.0,
    ssim_dynamic_range: float = 1.0,
    pretrained: bool = True,
    requires_grad: bool = False,
    clamp_min: float = -30.0,
    clamp_max: float = 20.0,
) -> LossFnSpec:
    """Returns a loss function.

    Args:
        loss: The loss function to use.
        huber_beta: The beta parameter for the Huber loss.
        sample_rate: The sample rate of the audio.
        f_min: The minimum frequency for the STFT loss.
        f_max: The maximum frequency for the STFT loss.
        fft_size: The size of the FFT.
        shift_size: The size of the shift.
        win_length: The size of the window.
        n_mels: The number of mel bins for the mel spectrogram loss.
        n_mfcc: The number of MFCCs for the MFCC loss.
        log_mels: Whether to use log-mel spectrograms for the MFCC loss.
        window_fn: The window function to use.
        fft_size_multiples: The multiples of the FFT size to use for the
            multi-resolution STFT loss.
        image_kernel_size: The size of the kernel for the SSIM loss.
        ssim_stride: The stride of the kernel for the SSIM loss.
        ssim_channels: The number of channels for the SSIM loss.
        ssim_mode: The mode for the SSIM loss, either ``"avg"`` or ``"sum"``.
        image_sigma: The sigma parameter for the SSIM loss.
        ssim_dynamic_range: The dynamic range parameter for the SSIM loss.
        pretrained: Whether to use pretrained weights for the loss function,
            if the loss function uses a pretrained model.
        requires_grad: Whether to require gradients for parameters in the loss
            function, for parameters which can be disabled.
        clamp_min: The minimum value to clamp the input to.
        clamp_max: The maximum value to clamp the input to.

    Returns:
        The loss function, as a callable that takes in the input tensor or
        tensors and returns the loss tensor or tensors.
    """
    match loss:
        case "mse":
            return nn.MSELoss(reduction="none")
        case "l1":
            return nn.L1Loss(reduction="none")
        case "huber":
            return nn.SmoothL1Loss(reduction="none", beta=huber_beta)
        case "log-cosh":
            return log_cosh_loss
        case "xent":
            return nn.CrossEntropyLoss(reduction="none")
        case "bce":
            return nn.BCELoss(reduction="none")
        case "bce-logits":
            return nn.BCEWithLogitsLoss(reduction="none")
        case "spectral-convergence":
            return spectral_convergence_loss
        case "log-stft-magnitude":
            return log_stft_magnitude_loss
        case "stft":
            return STFTLoss(
                fft_size=fft_size,
                shift_size=shift_size,
                win_length=win_length,
                window=window_fn,
            )
        case "multi-stft":
            return MultiResolutionSTFTLoss(
                fft_sizes=[int(fft_size * multiple) for multiple in fft_size_multiples],
                hop_sizes=[int(shift_size * multiple) for multiple in fft_size_multiples],
                win_lengths=[int(win_length * multiple) for multiple in fft_size_multiples],
                window=window_fn,
            )
        case "mel":
            return MelLoss(
                sample_rate=sample_rate,
                n_fft=fft_size,
                win_length=win_length,
                hop_length=shift_size,
                f_min=f_min,
                f_max=f_max,
                n_mels=n_mels,
                window=window_fn,
            )
        case "mfcc":
            return MFCCLoss(
                sample_rate=sample_rate,
                n_mfcc=n_mfcc,
                log_mels=log_mels,
                n_fft=fft_size,
                win_length=win_length,
                hop_length=shift_size,
                f_min=f_min,
                f_max=f_max,
                n_mels=n_mels,
                window=window_fn,
            )
        case "ssim":
            return SSIMLoss(
                kernel_size=image_kernel_size,
                stride=ssim_stride,
                channels=ssim_channels,
                mode=ssim_mode,
                sigma=image_sigma,
                dynamic_range=ssim_dynamic_range,
            )
        case "image-grad":
            return ImageGradLoss(
                kernel_size=image_kernel_size,
                sigma=image_sigma,
            )
        case "lpips":
            return LPIPS(
                pretrained=pretrained,
                requires_grad=requires_grad,
            )
        case "kl-single":
            return functools.partial(kl_div_single_loss, clamp_min=clamp_min, clamp_max=clamp_max)
        case "kl-pair":
            return functools.partial(kl_div_pair_loss, clamp_min=clamp_min, clamp_max=clamp_max)
        case _:
            raise NotImplementedError(f"Unexpected loss type: {loss}")
