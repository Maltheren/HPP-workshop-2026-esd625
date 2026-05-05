import numpy as np
from numba import jit, float32, int32, prange
from converters import create_dct_matrices, pad_and_partition_hw
import time

@jit(nopython=True)
def compress_kernel(bx, by, Partitions, dct_h, dct_w, mean, Q):
    if bx >= Partitions.shape[0] or by >= Partitions.shape[1]:
        return np.zeros((8, 8), dtype=np.float32)
    
    block = Partitions[bx, by]
    H = block.shape[0]
    W = block.shape[1]

    temp = np.empty((8, 8), dtype=np.float32)
    block2 = np.empty((8, 8), dtype=np.float32)
    pre_quantize = np.empty((8, 8), dtype=np.float32)  # var 38 før - typo!

    for i in range(H):
        for j in range(W):
            val = (block[i, j, 0] + block[i, j, 1] + block[i, j, 2]) / 3.0
            block2[i, j] = val - mean

    for i in range(H):
        for j in range(W):
            s = 0.0
            for k in range(W):
                s += dct_h[i, k] * block2[k, j]
            temp[i, j] = s

    for i in range(H):
        for j in range(W):
            s = 0.0
            for k in range(H):
                s += temp[i, k] * dct_w[j, k]
            pre_quantize[i, j] = s

    out = np.zeros((H, W), dtype=np.float32)
    for i in range(H):
        for j in range(W):
            out[i, j] = float32(int32(pre_quantize[i, j] / Q[i, j]))

    return out

##Please note im a bit lazy so we speed this up with an trampoline funciton

@jit(nopython=True, parallel=True)
def interstage_speedup(blocks_np, dct_matrix_height, dct_matrix_width, avg, Q, out):
    for x in prange(blocks_np.shape[0]):
        for y in range(blocks_np.shape[1]):
            out[x, y] = compress_kernel(x,y, blocks_np, dct_matrix_height, dct_matrix_width, avg, Q)

###Interface to process the blocks
def compress(img, Q, block_h, block_w):
    t_0 = time.perf_counter()
    blocks, avg = pad_and_partition_hw(img, block_h, block_w)

    blocks_np = np.array(blocks, dtype=np.float32)
    dct_matrix_height, dct_matrix_width = create_dct_matrices(8, 8)
    t_1 = time.perf_counter()
    t_setup = t_1 - t_0

    out = np.zeros(
        (blocks_np.shape[0], blocks_np.shape[1], block_h, block_w),
        dtype=np.float32
    )
    ##Precompile
    compress_kernel(0,0, blocks_np, dct_matrix_height, dct_matrix_width, avg, Q)
    interstage_speedup(blocks_np[0:1], dct_matrix_height, dct_matrix_width, avg, Q, out)

    t_0 = time.perf_counter()
    interstage_speedup(blocks_np, dct_matrix_height, dct_matrix_width, avg, Q, out)
    t_1 = time.perf_counter()

    t_meas = t_1 - t_0 

    return out, avg, t_setup, t_meas