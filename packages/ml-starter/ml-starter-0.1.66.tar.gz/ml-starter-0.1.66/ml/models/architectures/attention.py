"""Defines some attention architectures.

You can implement a self-attention model using the built-in PyTorch module:

.. code-block:: python

    from torch import nn

    self.attn = nn.TransformerEncoder(
        nn.TransformerEncoderLayer(
            d_model=512,
            nhead=8,
            dim_feedforward=2048,
            dropout=0.1,
            activation='relu',
            batch_first=True,
        ),
        num_layers=6,
    )

However, when doing inference, you will end up recomputing a lot of previous
states. Instead, you can use the equivalent implementation in this file:

.. code-block:: python

    from ml.models.architectures.attention import TransformerEncoder, TransformerEncoderLayer

    self.attn = TransformerEncoder(
        TransformerEncoderLayer(
            d_model=512,
            nhead=8,
            dim_feedforward=2048,
            dropout=0.1,
            # activation='relu',  Always ReLU
            # batch_first=True,  Always batch first
        ),
        num_layers=6,
    )

This also eliminates the need to pass in an attention mask; instead, simply use
the ``is_causal`` argument to the ``forward`` method and it will automatically
apply the mask for you.
"""

import copy
from typing import cast

import torch
import torch.nn.functional as F
from torch import Tensor, nn

MultiheadAttentionState = tuple[Tensor, Tensor]


class MultiheadAttention(nn.Module):
    """Defines a streamable multihead attention layer.

    This is a slightly modified implementation of ``nn.MultiheadAttention``
    that is built into PyTorch. The main difference is that this version
    supports streaming inference for causal attention, by passing in a
    state tuple that contains the previously projected key and value tensors.

    Parameters:
        embed_dim: The input and output embedding dimension.
        num_heads: The number of attention heads.
        dropout: The dropout probability, applied to the attention matrix.
        bias: Whether to include a bias term in the projection layers.
        kdim: The dimension of the key projection. Defaults to ``embed_dim``.
        vdim: The dimension of the value projection. Defaults to ``embed_dim``.

    Inputs:
        query: The query tensor, of shape ``(B, T, C)``.
        key: The key tensor, of shape ``(B, T, C)``.
        value: The value tensor, of shape ``(B, T, C)``.
        state: The previous key and value tensors, of shape
            ``(B * H, T', C // H)``, where ``T'`` is the number of previous
            timesteps and ``H`` is the number of attention heads. This is
            only supported if ``is_causal=True``.
        is_causal: Whether to apply a causal mask to the attention matrix.
            Note that the "mask" is only applied implicitly and isn't actually
            instantiated as a tensor.

    Outputs:
        output: The output tensor, of shape ``(B, T, C)``.
    """

    __constants__ = ["dropout", "head_dim", "_qkv_same_embed_dim"]

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.0,
        bias: bool = True,
        kdim: int | None = None,
        vdim: int | None = None,
    ) -> None:
        super().__init__()

        self.embed_dim = embed_dim
        self.kdim = kdim if kdim is not None else embed_dim
        self.vdim = vdim if vdim is not None else embed_dim
        self._qkv_same_embed_dim = self.kdim == embed_dim and self.vdim == embed_dim

        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads

        assert self.head_dim * num_heads == self.embed_dim, f"`{embed_dim=}` must be divisible by `{num_heads=}`"

        if not self._qkv_same_embed_dim:
            self.q_proj_weight = nn.Parameter(torch.empty((embed_dim, embed_dim)))
            self.k_proj_weight = nn.Parameter(torch.empty((embed_dim, self.kdim)))
            self.v_proj_weight = nn.Parameter(torch.empty((embed_dim, self.vdim)))
            self.register_parameter("in_proj_weight", None)
        else:
            self.in_proj_weight = nn.Parameter(torch.empty((3 * embed_dim, embed_dim)))
            self.register_parameter("q_proj_weight", None)
            self.register_parameter("k_proj_weight", None)
            self.register_parameter("v_proj_weight", None)

        if bias:
            self.in_proj_bias = nn.Parameter(torch.empty(3 * embed_dim))
        else:
            self.register_parameter("in_proj_bias", None)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        self._reset_parameters()

    def _reset_parameters(self) -> None:
        if self._qkv_same_embed_dim:
            nn.init.xavier_uniform_(self.in_proj_weight)
        else:
            nn.init.xavier_uniform_(self.q_proj_weight)
            nn.init.xavier_uniform_(self.k_proj_weight)
            nn.init.xavier_uniform_(self.v_proj_weight)

        if self.in_proj_bias is not None:
            nn.init.constant_(self.in_proj_bias, 0.0)
            nn.init.constant_(self.out_proj.bias, 0.0)

    def forward(
        self,
        query: Tensor,
        key: Tensor,
        value: Tensor,
        state: MultiheadAttentionState | None = None,
        is_causal: bool = False,
    ) -> tuple[Tensor, MultiheadAttentionState]:
        assert query.dim() == 3 and key.dim() == 3 and value.dim() == 3, "Input must be 3-dimensional"

        # Computes query, key, and value projections
        if self._qkv_same_embed_dim:
            qw, kw, vw = self.in_proj_weight.chunk(3, dim=0)
        else:
            qw, kw, vw = self.q_proj_weight, self.k_proj_weight, self.v_proj_weight
        qb, kb, vb = (None, None, None) if self.in_proj_bias is None else self.in_proj_bias.chunk(3)
        xq = F.linear(query, qw, qb)
        xk = F.linear(key, kw, kb)
        xv = F.linear(value, vw, vb)

        # Permutes (B, T, H * C) -> (B, H, T, C)
        xq = xq.unflatten(-1, (self.num_heads, self.head_dim)).transpose(1, 2)
        xk = xk.unflatten(-1, (self.num_heads, self.head_dim)).transpose(1, 2)
        xv = xv.unflatten(-1, (self.num_heads, self.head_dim)).transpose(1, 2)

        # Concatenates previous states
        if state is not None:
            prev_k, prev_v = state
            xk = torch.cat((prev_k, xk), dim=2)
            xv = torch.cat((prev_v, xv), dim=2)

        # Computes attention
        dropout = self.dropout if self.training else 0.0
        xo = F.scaled_dot_product_attention(xq, xk, xv, dropout_p=dropout, is_causal=is_causal)

        # Splits (B, H, T, C) -> (B, T, H * C)
        xo = xo.transpose(1, 2).flatten(2)

        # Applies output projection
        xo = self.out_proj(xo)

        return xo, (xk, xv)


class TransformerEncoderLayer(nn.Module):
    """Defines a transformer encoder layer.

    This layer is a drop-in replacement for ``nn.TransformerEncoderLayer``
    except that it returns the attention state for causal attention, which can
    be used to implement streaming inference.

    Parameters:
        d_model: The input and output embedding dimension.
        nhead: The number of attention heads.
        dim_feedforward: The dimension of the feedforward network.
        dropout: The dropout probability, applied to the attention matrix.
        layer_norm_eps: The layer normalization epsilon value.
        norm_first: Whether to apply layer normalization before the attention
            layer. Defaults to ``False``.

    Inputs:
        src: The input tensor, of shape ``(B, T, C)``.
        is_causal: Whether to apply a causal mask to the attention matrix.
            Note that the "mask" is only applied implicitly and isn't actually
            instantiated as a tensor.
        state: The previous key and value tensors, of shape
            ``(B * H, T', C // H)``, where ``T'`` is the number of previous
            timesteps and ``H`` is the number of attention heads. This is
            only supported if ``is_causal=True``.

    Outputs:
        output: The output tensor, of shape ``(B, T, C)``.
        state: The updated key and value tensors, of shape
            ``(B * H, T, C // H)``.
    """

    __constants__ = ["norm_first"]

    def __init__(
        self,
        d_model: int,
        nhead: int,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        layer_norm_eps: float = 1e-5,
        norm_first: bool = False,
    ) -> None:
        super().__init__()

        self.self_attn = MultiheadAttention(d_model, nhead, dropout=dropout)

        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm_first = norm_first
        self.norm1 = nn.LayerNorm(d_model, eps=layer_norm_eps)
        self.norm2 = nn.LayerNorm(d_model, eps=layer_norm_eps)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(
        self,
        src: Tensor,
        is_causal: bool = False,
        state: MultiheadAttentionState | None = None,
    ) -> tuple[Tensor, MultiheadAttentionState]:
        x = src
        if self.norm_first:
            xi, state = self._sa_block(self.norm1(x), state, is_causal)
            x = x + xi
            x = x + self._ff_block(self.norm2(x))
        else:
            xi, state = self._sa_block(x, state, is_causal)
            x = self.norm1(x + xi)
            x = self.norm2(x + self._ff_block(x))
        return x, state

    def _sa_block(
        self,
        x: Tensor,
        state: MultiheadAttentionState | None,
        is_causal: bool,
    ) -> tuple[Tensor, MultiheadAttentionState]:
        x, state = self.self_attn.forward(x, x, x, state, is_causal)
        return self.dropout1(x), state

    def _ff_block(self, x: Tensor) -> Tensor:
        x = self.linear2(self.dropout(self.activation(self.linear1(x))))
        return self.dropout2(x)


class TransformerEncoder(nn.Module):
    """Defines a transformer encoder.

    This is a drop-in replacement for ``nn.TransformerEncoder`` except that it
    returns the attention state for causal attention, which can be used to
    implement streaming inference.

    Parameters:
        encoder_layer: The encoder layer to use.
        num_layers: The number of encoder layers.
        norm: The normalization layer to use. Defaults to ``None``.

    Inputs:
        src: The input tensor, of shape ``(B, T, C)``.
        is_causal: Whether to apply a causal mask to the attention matrix.
            Note that the "mask" is only applied implicitly and isn't actually
            instantiated as a tensor.
        state: The previous key and value tensors, of shape
            ``(B * H, T', C // H)``, where ``T'`` is the number of previous
            timesteps and ``H`` is the number of attention heads. This is
            only supported if ``is_causal=True``.

    Outputs:
        output: The output tensor, of shape ``(B, T, C)``.
        state: The updated key and value tensors, of shape
            ``(B * H, T, C // H)``.
    """

    def __init__(
        self,
        encoder_layer: TransformerEncoderLayer,
        num_layers: int,
        norm: nn.LayerNorm | None = None,
    ) -> None:
        super().__init__()

        self.layers = cast(list[TransformerEncoderLayer], _get_clones(encoder_layer, num_layers))
        self.num_layers = num_layers
        self.norm = nn.Identity() if norm is None else norm

    def forward(
        self,
        src: Tensor,
        is_causal: bool = False,
        state: list[MultiheadAttentionState] | None = None,
    ) -> tuple[Tensor, list[MultiheadAttentionState] | None]:
        output = src
        state_out = []
        for i, layer in enumerate(self.layers):
            state_i = None if state is None else state[i]
            output, state_out_i = layer.forward(output, is_causal, state_i)
            if state_out_i is not None:
                state_out.append(state_out_i)
        return self.norm(output), None if len(state_out) == 0 else state_out


def nucleus_sampling(logits: Tensor, p: float, temperature: float = 1.0, dim: int = -1) -> Tensor:
    """Samples from a distribution using nucleus sampling.

    This is a modified version of ``torch.multinomial`` that uses nucleus
    sampling instead of top-k sampling. The difference is that top-k sampling
    sets the probability of all values outside the top-k to zero, whereas
    nucleus sampling sets the probability of all values outside the top-p
    to zero.

    Parameters:
        logits: The input tensor, of shape ``(B, T, C)``.
        p: The probability threshold.
        temperature: The temperature to apply to the logits.
        dim: The dimension to sample from. Defaults to ``-1``.

    Returns:
        The sampled indices, of shape ``(B, T)``.
    """
    assert 0.0 <= p <= 1.0, f"`{p=}` must be between 0 and 1"

    # Flattens logits to (N, C).
    if dim != -1:
        logits = logits.transpose(dim, -1)
    orig_shape = logits.shape[:-1]
    logits = logits.flatten(0, -2)

    # Sorts the logits in descending order
    sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)

    # Computes the cumulative probabilities
    cum_probs = torch.cumsum(F.softmax(sorted_logits / temperature, dim=-1), dim=-1)

    # Finds the top-p indices
    mask = cum_probs <= p
    mask[..., 1:] = mask[..., :-1].clone()
    mask[..., 0] = 1
    top_p_indices = sorted_indices.masked_fill(~mask, -1)

    # Samples from the top-p indices
    result = top_p_indices.gather(-1, torch.multinomial(cum_probs, 1))

    # Reshapes the result
    result = result.view(orig_shape)
    if dim != -1:
        result = result.transpose(dim, -1)
    return result


def _get_clones(module: TransformerEncoderLayer, num_layers: int) -> nn.ModuleList:
    return nn.ModuleList([copy.deepcopy(module) for _ in range(num_layers)])
