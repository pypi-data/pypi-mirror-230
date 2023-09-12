from typing import Optional

import torch

import _turbo_kernels as kernels

from ._utils import div_round_up, num_blocks_to_use


def lion8b_step_cuda(grads: torch.Tensor,
                     weights: torch.Tensor,
                     momentums: torch.Tensor,
                     scales: torch.Tensor,
                     lr: float,
                     beta1: float,
                     beta2: float,
                     weight_decay: float,
                     errors: Optional[torch.Tensor] = None) -> None:
    block_size = 128  # minimum value our impl allows
    grid_size: int = num_blocks_to_use(numel=weights.numel(),
                                       block_size=block_size,
                                       elems_per_thread=4)
    use_errors = (errors is not None) and (weights.dtype
                                           in (torch.float16, torch.bfloat16))

    shared_tensor_args = grads, weights, momentums, scales
    scalar_args = lr, beta1, beta2, weight_decay, grid_size, block_size
    if use_errors:
        kernels.lion8b_step_with_master_weights(*shared_tensor_args, errors,
                                                *scalar_args)
    else:
        kernels.lion8b_step_without_master_weights(*shared_tensor_args,
                                                   *scalar_args)


def lion8b_step(grads: torch.Tensor,
                weights: torch.Tensor,
                momentums: torch.Tensor,
                scales: torch.Tensor,
                lr: float,
                beta1: float,
                beta2: float,
                weight_decay: float,
                errors: Optional[torch.Tensor] = None) -> None:
    # just to save space in lists of allowed dtypes
    f16, bf16, f32 = torch.float16, torch.bfloat16, torch.float32

    use_errors = (errors is not None) and (weights.dtype in (f16, bf16))
    orig_shape = weights.shape

    # ------------------------------------------------ wall of error checking
    quantize_group_size = 32
    num_groups = div_round_up(weights.numel(), quantize_group_size)
    if (num_groups != scales.numel()):
        raise ValueError(f"Expected {num_groups} quantization scales but " +
                         f" received {scales.numel()}")

    for name, tensor, allowed_dtypes in [('grad', grads, (f16, bf16, f32)),
                                         ('param', weights, (f16, bf16, f32)),
                                         ('momentum', momentums, [torch.int8]),
                                         ('scales', scales, [f16]),
                                         ('errors', errors, [torch.uint8])]:
        if name == 'errors' and not use_errors:
            continue
        if not tensor.is_cuda:
            raise ValueError(
                f"{name} must be on a CUDA device, not {tensor.device}")
        if not tensor.is_contiguous():
            raise ValueError(f"{name} is not contiguous!")
        strides_unequal = tensor.stride() != weights.stride()
        if name not in ('scales', 'errors') and strides_unequal:
            raise ValueError(f"{name} stride {tensor.stride()} != " +
                             f"param stride {weights.stride()}")
        if tensor.dtype not in allowed_dtypes:
            raise ValueError(f"{name} must have dtype {allowed_dtypes}, not " +
                             f"{tensor.dtype}")
        if (name != 'scales') and (orig_shape != tensor.shape):
            raise ValueError(f"Param shape {orig_shape} != " +
                             f"{name} shape {tensor.shape}")

    if grads.dtype in (torch.float16, torch.bfloat16):
        allowed_dtypes = (grads.dtype, torch.float32)
        if weights.dtype not in allowed_dtypes:
            raise ValueError(
                f"Weights must be f32 or match grad dtype {grads.dtype}")

    # ------------------------------------------------ actual function calls
    return lion8b_step_cuda(grads=grads,
                            weights=weights,
                            momentums=momentums,
                            scales=scales,
                            lr=lr,
                            beta1=beta1,
                            beta2=beta2,
                            weight_decay=weight_decay,
                            errors=errors)
