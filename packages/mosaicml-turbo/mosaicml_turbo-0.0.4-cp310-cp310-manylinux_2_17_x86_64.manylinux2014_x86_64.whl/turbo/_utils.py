import functools

import torch


@functools.cache
def sm_count() -> int:
    props = torch.cuda.get_device_properties(torch.cuda.current_device())
    return props.multi_processor_count


def div_round_up(x: int, y: int) -> int:
    return (x + y - 1) // y


# cache the sm count and arithmetic since code is faster when we just
# call it with the right number of blocks. We normally use 32 blocks per
# SM since this is the minimal number that can run concurrently; this
# amortizes block creation + cleanup overhead
@functools.cache
def num_blocks_to_use(numel: int,
                      block_size: int,
                      elems_per_thread: int = 1) -> int:
    num_sms = sm_count()
    max_simultaneous_threads = num_sms * 2048  # always true for A100s
    max_simultaneous_blocks = num_sms * 32  # always true for A100s
    max_blocks_schedulable = div_round_up(max_simultaneous_threads, block_size)
    max_blocks_of_work = div_round_up(numel, block_size * elems_per_thread)
    max_blocks = min(max_simultaneous_blocks, max_blocks_schedulable)
    max_blocks = min(max_blocks, max_blocks_of_work)
    return max_blocks * 2  # the x2 isn't needed; just like 1% faster
