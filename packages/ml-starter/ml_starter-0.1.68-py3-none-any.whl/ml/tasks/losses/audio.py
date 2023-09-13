"""Defines some loss functions which are suitable for audio."""

import functools
import warnings
from typing import Literal, cast

import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torchaudio.transforms import MFCC, MelSpectrogram

WindowFn = Literal["hann", "hamming", "blackman"]


def get_window(window: WindowFn, win_length: int) -> Tensor:
    """Gets a window tensor from a function name.

    Args:
        window: The window function name.
        win_length: The window length.

    Returns:
        The window tensor, with shape ``(win_length)``.
    """
    match window:
        case "hann":
            return torch.hann_window(win_length)
        case "hamming":
            return torch.hamming_window(win_length)
        case "blackman":
            return torch.blackman_window(win_length)
        case _:
            raise NotImplementedError(f"Unexpected window type: {window}")


def stft(x: Tensor, fft_size: int, hop_size: int, win_length: int, window: Tensor) -> Tensor:
    """Perform STFT and convert to magnitude spectrogram.

    Args:
        x: Input signal tensor with shape ``(B, T)``.
        fft_size: FFT size.
        hop_size: Hop size.
        win_length: Window length.
        window: The window function.

    Returns:
        Magnitude spectrogram with shape ``(B, num_frames, fft_size // 2 + 1)``.
    """
    dtype = x.dtype
    if dtype == torch.bfloat16:
        x = x.float()
    x_stft = torch.stft(x, fft_size, hop_size, win_length, window, return_complex=True)
    real, imag = x_stft.real, x_stft.imag
    return torch.sqrt(torch.clamp(real**2 + imag**2, min=1e-7)).transpose(2, 1).to(dtype)


def spectral_convergence_loss(x_mag: Tensor, y_mag: Tensor, eps: float = 1e-8) -> Tensor:
    """Spectral convergence loss module.

    Args:
        x_mag: Magnitude spectrogram of predicted signal, with shape
            ``(B, num_frames, #=num_freq_bins)``.
        y_mag: Magnitude spectrogram of groundtruth signal, with shape
            ``(B, num_frames, num_freq_bins)``.
        eps: A small value to avoid division by zero.

    Returns:
        Spectral convergence loss value.
    """
    x_mag, y_mag = x_mag.float(), y_mag.float().clamp_min(eps)
    if y_mag.requires_grad:
        warnings.warn(
            "`y_mag` is the ground truth and should not require a gradient! "
            "`spectral_convergence_loss` is not a symmetric loss function."
        )
    return torch.norm(y_mag - x_mag, p="fro", dim=-1) / torch.norm(y_mag, p="fro", dim=-1)


def log_stft_magnitude_loss(x_mag: Tensor, y_mag: Tensor, eps: float = 1e-8) -> Tensor:
    """Log STFT magnitude loss module.

    Args:
        x_mag: Magnitude spectrogram of predicted signal
            ``(B, num_frames, num_freq_bins)``.
        y_mag: Magnitude spectrogram of groundtruth signal
            ``(B, num_frames, num_freq_bins)``.
        eps: A small value to avoid log(0).

    Returns:
        Tensor: Log STFT magnitude loss value.
    """
    x_mag, y_mag = x_mag.float().clamp_min(eps), y_mag.float().clamp_min(eps)
    return F.l1_loss(torch.log(y_mag), torch.log(x_mag), reduction="none").mean(-1)


def stft_magnitude_loss(x_mag: Tensor, y_mag: Tensor) -> Tensor:
    """STFT magnitude loss module.

    Args:
        x_mag: Magnitude spectrogram of predicted signal
            ``(B, num_frames, num_freq_bins)``.
        y_mag: Magnitude spectrogram of groundtruth signal
            ``(B, num_frames, num_freq_bins)``.

    Returns:
        Tensor: STFT magnitude loss value.
    """
    return F.l1_loss(y_mag, x_mag, reduction="none").mean(-1)


class STFTLoss(nn.Module):
    r"""Defines a STFT loss function.

    This function returns two losses which are roughly equivalent, one for
    minimizing the spectral distance and one for minimizing the log STFT
    magnitude distance. The spectral convergence loss is defined as:

    .. math::

        L_{spec} = \\frac{\\|Y - X\\|_F}{\\|Y\\|_F}

    where :math:`X` and :math:`Y` are the predicted and groundtruth STFT
    spectrograms, respectively. The log STFT magnitude loss is defined as:

    .. math::

        L_{mag} = \\frac{\\|\\log Y - \\log X\\|_1}{N}

    Parameters:
        fft_size: FFT size, meaning the number of Fourier bins.
        shift_size: Shift size in sample.
        win_length: Window length in sample.
        window: Window function type. Choices are ``hann``, ``hamming`` and
            ``blackman``.

    Inputs:
        x: Predicted signal ``(B, T)``.
        y: Groundtruth signal ``(B, T)``.

    Outputs:
        Spectral convergence loss value and log STFT magnitude loss value.
    """

    window: Tensor

    def __init__(
        self,
        fft_size: int = 1024,
        shift_size: int = 120,
        win_length: int = 600,
        window: WindowFn = "hann",
    ) -> None:
        super().__init__()

        self.fft_size = fft_size
        self.shift_size = shift_size
        self.win_length = win_length
        self.register_buffer("window", get_window(window, win_length))

    def forward(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        x_mag = stft(x, self.fft_size, self.shift_size, self.win_length, self.window)
        y_mag = stft(y, self.fft_size, self.shift_size, self.win_length, self.window)
        sc_loss = spectral_convergence_loss(x_mag, y_mag)
        mag_loss = log_stft_magnitude_loss(x_mag, y_mag)
        return sc_loss, mag_loss


class MultiResolutionSTFTLoss(nn.Module):
    """Multi resolution STFT loss module.

    Parameters:
        fft_sizes: List of FFT sizes.
        hop_sizes: List of hop sizes.
        win_lengths: List of window lengths.
        window: Window function type. Choices are ``hann``, ``hamming`` and
            ``blackman``.
        factor_sc: A balancing factor across different losses.
        factor_mag: A balancing factor across different losses.

    Inputs:
        x: Predicted signal (B, T).
        y: Groundtruth signal (B, T).

    Outputs:
        Multi resolution spectral convergence loss value, and multi resolution
        log STFT magnitude loss value.
    """

    def __init__(
        self,
        fft_sizes: list[int] = [1024, 2048, 512],
        hop_sizes: list[int] = [120, 240, 60],
        win_lengths: list[int] = [600, 1200, 300],
        window: WindowFn = "hann",
        factor_sc: float = 1.0,
        factor_mag: float = 1.0,
    ) -> None:
        super().__init__()

        assert len(fft_sizes) == len(hop_sizes) == len(win_lengths)
        assert len(fft_sizes) > 0

        self.stft_losses = cast(list[STFTLoss], nn.ModuleList())
        for fs, ss, wl in zip(fft_sizes, hop_sizes, win_lengths):
            self.stft_losses += [STFTLoss(fs, ss, wl, window)]
        self.factor_sc = factor_sc
        self.factor_mag = factor_mag

    def forward(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        sc_loss: Tensor | None = None
        mag_loss: Tensor | None = None

        for f in self.stft_losses:
            sc_l, mag_l = f(x, y)
            sc_l, mag_l = sc_l.flatten(1).mean(1), mag_l.flatten(1).mean(1)
            sc_loss = sc_l if sc_loss is None else sc_loss + sc_l
            mag_loss = mag_l if mag_loss is None else mag_loss + mag_l

        assert sc_loss is not None
        assert mag_loss is not None

        sc_loss /= len(self.stft_losses)
        mag_loss /= len(self.stft_losses)

        return self.factor_sc * sc_loss, self.factor_mag * mag_loss


class MelLoss(nn.Module):
    """Defines a Mel loss function.

    This module is similar to ``STFTLoss``, but it uses mel spectrogram instead
    of the regular STFT, which may be more suitable for speech.

    Parameters:
        sample_rate: Sample rate of the input signal.
        n_fft: FFT size.
        win_length: Window length.
        hop_length: Hop size.
        f_min: Minimum frequency.
        f_max: Maximum frequency.
        n_mels: Number of mel bins.
        window: Window function name.
        power: Exponent for the magnitude spectrogram.
        normalized: Whether to normalize by number of frames.

    Inputs:
        x: Predicted signal ``(B, T)``.
        y: Groundtruth signal ``(B, T)``.

    Outputs:
        Spectral convergence loss value and log mel spectrogram loss value.
    """

    __constants__ = ["eps"]

    def __init__(
        self,
        sample_rate: int,
        n_fft: int = 400,
        win_length: int | None = None,
        hop_length: int | None = None,
        f_min: float = 0.0,
        f_max: float | None = None,
        n_mels: int = 80,
        window: WindowFn = "hann",
        power: float = 1.0,
        normalized: bool = False,
        eps: float = 1e-7,
    ) -> None:
        super().__init__()

        self.mel_fn = MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            f_min=f_min,
            f_max=f_max,
            n_mels=n_mels,
            window_fn=functools.partial(get_window, window),
            power=power,
            normalized=normalized,
        )

        self.eps = eps

    def forward(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        x_mag, y_mag = self.mel_fn(x), self.mel_fn(y)
        return spectral_convergence_loss(x_mag, y_mag, self.eps), log_stft_magnitude_loss(x_mag, y_mag, self.eps)


class MFCCLoss(nn.Module):
    """Defines an MFCC loss function.

    This is similar to ``MelLoss``, but it uses MFCC instead of mel spectrogram.
    MFCCs are like the "spectrum of a spectrum" which are usually just used to
    compress the representation. In the context of a loss function it should
    be largely equivalent to the mel spectrogram, although it may be more
    robust to noise.

    Parameters:
        sample_rate: Sample rate of the input signal.
        n_mfcc: Number of MFCCs.
        dct_type: DCT type.
        norm: Norm type.
        log_mels: Whether to use log-mel spectrograms instead of mel.
        n_fft: FFT size, for Mel spectrogram.
        win_length: Window length, for Mel spectrogram.
        hop_length: Hop size, for Mel spectrogram.
        f_min: Minimum frequency, for Mel spectrogram.
        f_max: Maximum frequency, for Mel spectrogram.
        n_mels: Number of mel bins, for Mel spectrogram.
        window: Window function name, for Mel spectrogram.

    Inputs:
        x: Predicted signal ``(B, T)``.
        y: Groundtruth signal ``(B, T)``.

    Outputs:
        Spectral convergence loss value and log mel spectrogram loss value.
    """

    def __init__(
        self,
        sample_rate: int,
        n_mfcc: int = 40,
        dct_type: int = 2,
        norm: str | None = "ortho",
        log_mels: bool = False,
        n_fft: int = 400,
        win_length: int | None = None,
        hop_length: int | None = None,
        f_min: float = 0.0,
        f_max: float | None = None,
        n_mels: int = 80,
        window: WindowFn = "hann",
    ) -> None:
        super().__init__()

        self.mfcc_fn = MFCC(
            sample_rate=sample_rate,
            n_mfcc=n_mfcc,
            dct_type=dct_type,
            norm=norm,
            log_mels=log_mels,
            melkwargs={
                "n_fft": n_fft,
                "win_length": win_length,
                "hop_length": hop_length,
                "f_min": f_min,
                "f_max": f_max,
                "n_mels": n_mels,
                "window_fn": functools.partial(get_window, window),
            },
        )

    def forward(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        x_mfcc, y_mfcc = self.mfcc_fn(x), self.mfcc_fn(y)
        return spectral_convergence_loss(x_mfcc, y_mfcc), log_stft_magnitude_loss(x_mfcc, y_mfcc)
