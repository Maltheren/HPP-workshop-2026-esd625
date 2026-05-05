import numpy as np
from converters import pad_and_partition_hw, create_dct_matrices
import time


def compress_kernel(bx, by, Partitions, dct_h, dct_w, mean, Q):

    if bx < Partitions.shape[0] and by < Partitions.shape[1]:

        block = Partitions[bx, by]

        H = block.shape[0]
        W = block.shape[1]

        # ---- local buffer ----
        temp = np.empty((8, 8), dtype=np.float32)
        block2 = np.empty((8, 8), dtype=np.float32)
        pre_quantize = np.empty((8, 38), dtype=np.float32)

        # Runs the averaging of the colors and subtracts the given mean for the whole picture
        for i in range(H):
            for j in range(W):
                val = (block[i, j, 0] + block[i, j, 1] + block[i, j, 2]) / 3.0
                block2[i, j] = val - mean

        # Does the DCT on the rows
        for i in range(H):
            for j in range(W):
                s = 0.0
                for k in range(W):
                    s += dct_h[i, k] * block2[k, j]
                temp[i, j] = s

        # Same stuff but instead our Coloumns 
        for i in range(H):
            for j in range(W):
                s = 0.0
                for k in range(H):
                    s += temp[i, k] * dct_w[j, k]  
                pre_quantize[i, j] = s

        out = np.zeros([H, W], dtype=np.float32)

        ##With a bit of luck we got the DCT of each box now...
        ###This one here is stolen from the internet i dont remember where (The Q matrix)
        for i in range(H):
            for j in range(W):
                out[i, j] =  round(pre_quantize[i,j] / Q[i, j]) #pre_quantize[i, j] # round(pre_quantize[i,j] / Q[i, j])
        return out

def compress(img, Q, block_h, block_w):
    t_0 = time.perf_counter()
    blocks, avg = pad_and_partition_hw(img, block_h, block_w)

    threads_per_block = (16, 16)
    blocks_np = np.array(blocks, dtype=np.float32)
    dct_matrix_height, dct_matrix_width = create_dct_matrices(8, 8)
    t_1 = time.perf_counter()
    t_setup = t_1 - t_0

    out = np.zeros(
        (blocks_np.shape[0], blocks_np.shape[1], block_h, block_w),
        dtype=np.float32
    )
    
    t_0 = time.perf_counter()
    for x in range(blocks_np.shape[0]):
        for y in range(blocks_np.shape[1]):
            out[x, y] = compress_kernel(x,y, blocks_np, dct_matrix_height, dct_matrix_width, avg, Q)
    t_1 = time.perf_counter()
    t_meas = t_1 - t_0 

    return out, avg, t_setup, t_meas