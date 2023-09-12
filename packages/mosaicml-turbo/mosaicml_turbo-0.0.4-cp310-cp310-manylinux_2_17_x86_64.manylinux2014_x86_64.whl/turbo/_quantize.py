from typing import Optional, Tuple

import torch

import _turbo_kernels as kernels

from ._utils import div_round_up, num_blocks_to_use

_GROUP_SIZE = 32
_BLOCK_SIZE = 256
_scales_dtype = torch.float16


class ElemwiseOps:
    IDENTITY = 'identity'
    GELU_FORWARD = 'gelu_forward'
    GELU_BACKWARD = 'gelu_backward'

    ALL_FORWARD_OPS = (IDENTITY, GELU_FORWARD)
    ALL_BACKWARD_OPS = (GELU_BACKWARD,)
    ALL_OPS = ALL_FORWARD_OPS + ALL_FORWARD_OPS


_op_to_int = {
    ElemwiseOps.IDENTITY: 0,
    ElemwiseOps.GELU_FORWARD: 1,
    ElemwiseOps.GELU_BACKWARD: 2,
}


def _check_quantize_inputs(x_f: torch.Tensor,
                           scales: torch.Tensor,
                           x_q: torch.Tensor,
                           x_forward: Optional[torch.Tensor] = None) -> None:
    # device and layout checks
    for name, tensor in [('x_not_quantized', x_f), ('scales', scales),
                         ('x_quantized', x_q), ('x_forward', x_forward)]:
        if name == 'x_forward' and tensor is None:
            continue
        if not tensor.is_cuda:
            raise NotImplementedError('Quantization only supported for CUDA ' +
                                      f'tensors. {name} device={tensor.device}')
        if tensor.device != x_f.device:
            raise ValueError(f'{name} device {tensor.device} != ' +
                             f'non-quantized device {x_f.device}')
        if not tensor.is_contiguous():
            raise ValueError(f'{name} is not contiguous')

    # dtype checks
    if x_f.dtype not in (torch.float16, torch.bfloat16, torch.float32):
        raise NotImplementedError(
            'Only [de]quantization of float16, bfloat16, and float32 ' +
            f'are supported; got {x_f.dtype}')
    if scales.dtype != torch.float16:
        raise NotImplementedError(f'Scales must be float16, not {scales.dtype}')
    if x_q.dtype != torch.int8:
        raise ValueError(f'Quantized tensor must be int8, not {x_q.dtype}')
    if x_forward is not None and x_forward.dtype != x_f.dtype:
        raise NotImplementedError(
            f'Elemwise op output tensor dtype {x_forward.dtype} does not '
            f'match input dtype {x_f.dtype}')


def _check_num_bits(num_bits: int) -> None:
    if num_bits not in (4, 8):
        raise ValueError(f'num_bits must be 4 or 8; got {num_bits}')


def quantize_signed(x: torch.Tensor,
                    num_bits: int = 8,
                    op: int = ElemwiseOps.IDENTITY,
                    scales_out: Optional[torch.Tensor] = None,
                    x_q_out: Optional[torch.Tensor] = None,
                    x_forward: Optional[torch.Tensor] = None):
    _check_num_bits(num_bits)
    input_size = x.numel()

    if x_q_out is None:
        x_q_shape = x.shape
        if num_bits == 4:  # we can't preserve shape, so just flatten
            x_q_shape = div_round_up(x.numel(), 2)
        x_q_out = torch.empty(
            x_q_shape, dtype=torch.int8, device=x.device, layout=x.layout)
    if scales_out is None:
        scales_out = torch.empty(div_round_up(input_size, _GROUP_SIZE),
                                 dtype=_scales_dtype,
                                 device=x.device)
    if x_forward is None:
        x_forward = x if op == ElemwiseOps.IDENTITY else torch.empty_like(x)

    _check_quantize_inputs(x, scales_out, x_q_out, x_forward=x_forward)

    op_int = _op_to_int[op]
    grid_size = num_blocks_to_use(input_size, _BLOCK_SIZE)
    kernels.quantize_signed(
        x, scales_out, x_q_out, x_forward, num_bits, op_int, grid_size)

    if op == ElemwiseOps.IDENTITY:
        # return x_q_out, scales_out, None  # TODO update lion unfused code
        return x_q_out, scales_out
    return x_q_out, scales_out, x_forward


def dequantize_signed(x_q: torch.Tensor,
                      scales: torch.Tensor,
                      num_bits: int = 8,
                      op: int = ElemwiseOps.IDENTITY,
                      x_out: Optional[torch.Tensor] = None,
                      out_shape: Optional[Tuple[int, ...]] = None,
                      out_dtype: torch.dtype = torch.float32) -> torch.Tensor:
    _check_num_bits(num_bits)
    input_size = x_q.numel()

    if x_out is None:
        shape = out_shape
        if shape is None:
            if num_bits == 8:
                shape = x_q.shape
            else:
                raise ValueError(
                    'Must specify either x_out or out_shape when quantizing ' +
                    'with <8 bits since sub-byte quantization cannot ' +
                    'preserve the original shape.')
        x_out = torch.empty(
            shape, dtype=out_dtype, device=x_q.device, layout=x_q.layout)
    _check_quantize_inputs(x_out, scales, x_q)

    op_int = _op_to_int[op]
    grid_size = num_blocks_to_use(input_size, _BLOCK_SIZE)
    kernels.dequantize_signed(x_q, scales, x_out, num_bits, op_int, grid_size)

    return x_out

# TODO rm after changing lion8b + pinning turbo version
quantize8b = quantize_signed
dequantize8b = dequantize_signed
