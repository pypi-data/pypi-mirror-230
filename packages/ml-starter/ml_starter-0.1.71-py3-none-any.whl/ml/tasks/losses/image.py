"""Defines some loss functions which are suitable for images."""

import math
from typing import Literal, cast

import torch
import torch.nn.functional as F
import torchvision
from torch import Tensor, nn

SsimFn = Literal["avg", "std"]


class SSIMLoss(nn.Module):
    """Computes structural similarity loss (SSIM).

    The `dynamic_range` is the difference between the maximum and minimum
    possible values for the image. This value is the actually the negative
    SSIM, so that minimizing it maximizes the SSIM score.

    Parameters:
        kernel_size: Size of the Gaussian kernel.
        stride: Stride of the Gaussian kernel.
        channels: Number of channels in the image.
        mode: Mode of the SSIM function, either ``avg`` or ``std``. The
            ``avg`` mode uses unweighted ``(K, K)`` regions, while the ``std``
            mode uses Gaussian weighted ``(K, K)`` regions, which allows for
            larger regions without worrying about blurring.
        sigma: Standard deviation of the Gaussian kernel.
        dynamic_range: Difference between the maximum and minimum possible
            values for the image.

    Inputs:
        x: float tensor with shape ``(B, C, H, W)``
        y: float tensor with shape ``(B, C, H, W)``

    Outputs:
        float tensor with shape ``(B, C, H - K + 1, W - K + 1)``
    """

    def __init__(
        self,
        kernel_size: int = 3,
        stride: int = 1,
        channels: int = 3,
        mode: SsimFn = "avg",
        sigma: float = 1.0,
        dynamic_range: float = 1.0,
    ) -> None:
        super().__init__()

        self.c1 = (0.01 * dynamic_range) ** 2
        self.c2 = (0.03 * dynamic_range) ** 2

        match mode:
            case "avg":
                window = self.get_avg_window(kernel_size)
            case "std":
                window = self.get_gaussian_window(kernel_size, sigma)
            case _:
                raise NotImplementedError(f"Unexpected mode: {mode}")

        window = window.expand(channels, 1, kernel_size, kernel_size)
        self.window = nn.Parameter(window.clone(), requires_grad=False)
        self.stride = stride

    def get_gaussian_window(self, ksz: int, sigma: float) -> Tensor:
        x = torch.linspace(-(ksz // 2), ksz // 2, ksz)
        num = (-0.5 * (x / float(sigma)) ** 2).exp()
        denom = sigma * math.sqrt(2 * math.pi)
        window_1d = num / denom
        return window_1d[:, None] * window_1d[None, :]

    def get_avg_window(self, ksz: int) -> Tensor:
        return torch.full((ksz, ksz), 1 / (ksz**2))

    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        x = x.flatten(0, -4)
        y = y.flatten(0, -4)

        channels = x.size(1)
        mu_x = F.conv2d(x, self.window, groups=channels, stride=self.stride)
        mu_y = F.conv2d(y, self.window, groups=channels, stride=self.stride)
        mu_x_sq, mu_y_sq, mu_xy = mu_x**2, mu_y**2, mu_x * mu_y

        sigma_x = F.conv2d(x**2, self.window, groups=channels, stride=self.stride) - mu_x_sq
        sigma_y = F.conv2d(y**2, self.window, groups=channels, stride=self.stride) - mu_y_sq
        sigma_xy = F.conv2d(x * y, self.window, groups=channels, stride=self.stride) - mu_xy

        num_a = 2 * mu_x * mu_y + self.c1
        num_b = 2 * sigma_xy + self.c2
        denom_a = mu_x_sq + mu_y_sq + self.c1
        denom_b = sigma_x**2 + sigma_y**2 + self.c2

        score = (num_a * num_b) / (denom_a * denom_b)
        return -score


class ImageGradLoss(nn.Module):
    """Computes image gradients, for smoothing.

    This function convolves the image with a special Gaussian kernel that
    contrasts the current pixel with the surrounding pixels, such that the
    output is zero if the current pixel is the same as the surrounding pixels,
    and is larger if the current pixel is different from the surrounding pixels.

    Parameters:
        kernel_size: Size of the Gaussian kernel.
        sigma: Standard deviation of the Gaussian kernel.

    Inputs:
        x: float tensor with shape ``(B, C, H, W)``

    Outputs:
        float tensor with shape ``(B, C, H - ksz + 1, W - ksz + 1)``
    """

    kernel: Tensor

    def __init__(self, kernel_size: int = 3, sigma: float = 1.0) -> None:
        super().__init__()

        assert kernel_size % 2 == 1, "Kernel size must be odd"
        assert kernel_size > 1, "Kernel size must be greater than 1"

        self.kernel_size = kernel_size
        self.register_buffer("kernel", self.get_kernel(kernel_size, sigma), persistent=False)

    def get_kernel(self, ksz: int, sigma: float) -> Tensor:
        x = torch.linspace(-(ksz // 2), ksz // 2, ksz)
        num = (-0.5 * (x / float(sigma)) ** 2).exp()
        denom = sigma * math.sqrt(2 * math.pi)
        window_1d = num / denom
        window = window_1d[:, None] * window_1d[None, :]
        window[ksz // 2, ksz // 2] = 0
        window = window / window.sum()
        window[ksz // 2, ksz // 2] = -1.0
        return window.unsqueeze(0).unsqueeze(0)

    def forward(self, x: Tensor) -> Tensor:
        channels = x.size(1)
        return F.conv2d(x, self.kernel.repeat_interleave(channels, 0), stride=1, padding=0, groups=channels)


class _Scale(nn.Module):
    def __init__(
        self,
        shift: tuple[float, float, float] = (-0.030, -0.088, -0.188),
        scale: tuple[float, float, float] = (0.458, 0.488, 0.450),
    ) -> None:
        super().__init__()

        self.register_buffer("shift", torch.tensor(shift, dtype=torch.float32).view(1, -1, 1, 1))
        self.register_buffer("scale", torch.tensor(scale, dtype=torch.float32).view(1, -1, 1, 1))

    shift: Tensor
    scale: Tensor

    def forward(self, x: Tensor) -> Tensor:
        return x * self.scale + self.shift


class _VGG16(nn.Module):
    def __init__(self, pretrained: bool = True, requires_grad: bool = False) -> None:
        super().__init__()

        features = torchvision.models.vgg16(pretrained=pretrained).features

        self.slice1 = nn.Sequential()
        self.slice2 = nn.Sequential()
        self.slice3 = nn.Sequential()
        self.slice4 = nn.Sequential()
        self.slice5 = nn.Sequential()

        for x in range(4):
            self.slice1.add_module(str(x), features[x])
        for x in range(4, 9):
            self.slice2.add_module(str(x), features[x])
        for x in range(9, 16):
            self.slice3.add_module(str(x), features[x])
        for x in range(16, 23):
            self.slice4.add_module(str(x), features[x])
        for x in range(23, 30):
            self.slice5.add_module(str(x), features[x])

        if not requires_grad:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
        h = self.slice1(x)
        h_relu1_2 = h
        h = self.slice2(h)
        h_relu2_2 = h
        h = self.slice3(h)
        h_relu3_3 = h
        h = self.slice4(h)
        h_relu4_3 = h
        h = self.slice5(h)
        h_relu5_3 = h
        return h_relu1_2, h_relu2_2, h_relu3_3, h_relu4_3, h_relu5_3


class LPIPS(nn.Module):
    """Computes the learned perceptual image patch similarity (LPIPS) loss.

    This function extracts the VGG-16 features from each input image, projects
    them once, then computes the L2 distance between the projected features.

    The input images should be in the range ``[0, 1]``. The height and width of
    the input images should be at least 64 pixels but can otherwise be
    arbitrary.

    Parameters:
        pretrained: Whether to use the pretrained VGG-16 model. This should
            usually only be disabled for testing.
        requires_grad: Whether to require gradients for the VGG-16 model. This
            should usually be disabled, unless you want to fine-tune the model.
        dropout: Dropout probability for the input projections.

    Inputs:
        image_a: float tensor with shape ``(B, C, H, W)``
        image_b: float tensor with shape ``(B, C, H, W)``

    Outputs:
        float tensor with shape ``(B,)``
    """

    def __init__(self, pretrained: bool = True, requires_grad: bool = False, dropout: float = 0.5) -> None:
        super().__init__()

        # Loads the VGG16 model.
        self.vgg16 = _VGG16(pretrained=pretrained, requires_grad=requires_grad)

        # Scaling layer.
        self.scale = _Scale()

        # Input projections.
        self.in_projs = cast(
            list[nn.Conv2d],
            nn.ModuleList(
                [
                    self._in_proj(64, dropout=dropout),
                    self._in_proj(128, dropout=dropout),
                    self._in_proj(256, dropout=dropout),
                    self._in_proj(512, dropout=dropout),
                    self._in_proj(512, dropout=dropout),
                ]
            ),
        )

    def _in_proj(self, in_channels: int, out_channels: int = 1, dropout: float = 0.5) -> nn.Module:
        if dropout > 0:
            return nn.Sequential(
                nn.Dropout(p=dropout),
                nn.Conv2d(in_channels, out_channels, 1, bias=False),
            )
        return nn.Conv2d(in_channels, out_channels, 1, bias=False)

    def _normalize(self, x: Tensor, eps: float = 1e-10) -> Tensor:
        norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
        return x / (norm_factor + eps)

    def forward(self, image_a: Tensor, image_b: Tensor) -> Tensor:
        image_a, image_b = self.scale(image_a), self.scale(image_b)

        h0_a, h1_a, h2_a, h3_a, h4_a = self.vgg16(image_a)
        h0_b, h1_b, h2_b, h3_b, h4_b = self.vgg16(image_b)

        losses: list[Tensor] = []
        for in_proj, (a, b) in zip(
            self.in_projs,
            ((h0_a, h0_b), (h1_a, h1_b), (h2_a, h2_b), (h3_a, h3_b), (h4_a, h4_b)),
        ):
            diff = (self._normalize(a) - self._normalize(b)).pow(2)
            losses.append(in_proj.forward(diff).mean(dim=(2, 3)))

        return torch.stack(losses, dim=-1).sum(dim=-1).squeeze(1)
