# flake8: noqa: E501
"""Defines KL-divergence utility functions."""

from torch import Tensor


def kl_div_single_loss(mu: Tensor, log_var: Tensor, *, clamp_min: float = -30.0, clamp_max: float = 20.0) -> Tensor:
    r"""Computes the KL-divergence loss for a single Gaussian distribution.

    This loss minimizes the KL-divergence between the given distribution and a
    standard normal distribution. This can be expressed as:

    .. math::

        \frac{1}{2} \sum_{i=1}^d \left( \mu_i^2 + \sigma_i^2 - \log \sigma_i^2 - 1 \right)

    One way of interpretting KL-divergence used here is as the amount of
    information lost when the standard normal distribution is used to
    approximate the given distribution. In other words, by minimizing this loss,
    we are trying to make the given distribution have the same amount of
    information as the standard normal distribution. This is useful for
    things like variational autoencoders, where we want to make the latent
    distribution as close to a standard normal distribution as possible,
    so that we can sample from the normal distribution.

    Args:
        mu: The mean of the Gaussian distribution.
        log_var: The log variance of the Gaussian distribution.
        clamp_min: The minimum value to clamp the log variance to.
        clamp_max: The maximum value to clamp the log variance to.

    Returns:
        The KL-divergence loss.
    """
    log_var = log_var.clamp(min=clamp_min, max=clamp_max)
    var = log_var.exp()
    return -0.5 * (1 + log_var - mu.pow(2) - var)


def kl_div_pair_loss(
    mu_p: Tensor,
    log_var_p: Tensor,
    mu_q: Tensor,
    log_var_q: Tensor,
    *,
    clamp_min: float = -30.0,
    clamp_max: float = 20.0,
) -> Tensor:
    r"""Computes the KL-divergence loss for a pair of Gaussian distributions.

    This loss minimizes the KL-divergence between the first distribution and the
    second distribution. This can be expressed as:

    .. math::

        D_{KL}(p || q) = \sum_{i=1}^d \log \left( \frac{\sigma_{q,i}^2}{\sigma_{p,i}^2} \right) + \frac{\sigma_{p,i}^2 + (\mu_{p,i} - \mu_{q,i})^2}{\sigma_{q,i}^2} - \frac{1}{2}

    One way of interpretting KL-divergence is as the amount of information lost
    when the second distribution is used to approximate the first distribution.
    Thus, the loss is not symmetric.

    Args:
        mu_p: The mean of the first Gaussian distribution.
        log_var_p: The log variance of the first Gaussian distribution.
        mu_q: The mean of the second Gaussian distribution.
        log_var_q: The log variance of the second Gaussian distribution.
        clamp_min: The minimum value to clamp the log variance to.
        clamp_max: The maximum value to clamp the log variance to.

    Returns:
        The KL-divergence loss.
    """
    log_var_p = log_var_p.clamp(min=clamp_min, max=clamp_max)
    log_var_q = log_var_q.clamp(min=clamp_min, max=clamp_max)
    var1 = log_var_p.exp()
    var2 = log_var_q.exp()
    return (log_var_q - log_var_p) + (var1 + (mu_p - mu_q).pow(2)) / var2 - 0.5
