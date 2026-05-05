
import numpy as np
from numba import cuda, float32
from converters import create_dct_matrices, pad_and_partition_hw
import time


@cuda.jit
def compress_kernel(Partitions, dct_h, dct_w, mean, out, Q):

    bx, by = cuda.grid(2)

    if bx < Partitions.shape[0] and by < Partitions.shape[1]:

        block = Partitions[bx, by]

        H = block.shape[0]
        W = block.shape[1]

        # ---- local buffer ----
        temp = cuda.local.array((32, 32), dtype=float32)
        block2 = cuda.local.array((32, 32), dtype=float32)
        pre_quantize = cuda.local.array((32, 32), dtype=float32)

        # Runs the averaging of the colors and subtracts the given mean for the whole picture
        for i in range(H):
            for j in range(W):
                val = (block[i, j, 0] + block[i, j, 1] + block[i, j, 2]) / 3.0
                block2[i, j] = val - mean[0]

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

        
        ##With a bit of luck we got the DCT of each box now...
        ###This one here is stolen from the internet i dont remember where (The Q matrix)
        for i in range(H):
            for j in range(W):
                out[bx, by, i, j] =  round(pre_quantize[i,j] / Q[i, j]) #pre_quantize[i, j] # round(pre_quantize[i,j] / Q[i, j])


def compress(img, Q, block_h, block_w):
    blocks, avg = pad_and_partition_hw(img, block_h, block_w)


    threads_per_block = (16, 16)
    blocks_np = np.array(blocks, dtype=np.float32)
    blocks_per_grid_x = np.uint64((blocks_np.shape[0] + 15) // 16)
    blocks_per_grid_y = np.uint64((blocks_np.shape[1] + 15) // 16)


    dct_matrix_height, dct_matrix_width = create_dct_matrices(8, 8)
    ##Placeholder for some output image
    out = np.zeros(
        (blocks_np.shape[0], blocks_np.shape[1], block_h, block_w),
        dtype=np.float32
    )

    ##Throws relevant data to the GPU
    t_0 = time.perf_counter()
    cuda_avg =          cuda.to_device(np.array([avg], dtype=np.float32))
    cuda_img =          cuda.to_device(blocks_np)
    cuda_dct_matrix_h = cuda.to_device(dct_matrix_height)
    cuda_dct_matrix_w = cuda.to_device(dct_matrix_width)
    cuda_Q =            cuda.to_device(Q.astype(np.float32))
    d_out =             cuda.to_device(out)
    cuda.synchronize()
    t_1 = time.perf_counter()

    t_setup = t_1 -t_0
    ###Here we are doing a little sketchy thing for each test... we are wether we like it or not using numba so we call the kernel to initiate jit
    compress_kernel[
        (blocks_per_grid_x, blocks_per_grid_y),
        threads_per_block
    ](cuda_img, cuda_dct_matrix_h, cuda_dct_matrix_w, cuda_avg, d_out, cuda_Q)
    d_out = cuda.to_device(out) ##tømmer lige billedet igen
    cuda.synchronize()


    start = cuda.event()
    end = cuda.event()

    start.record()
    cuda_img = cuda.to_device(blocks_np)
    compress_kernel[
        (blocks_per_grid_x, blocks_per_grid_y),
        threads_per_block
    ](cuda_img, cuda_dct_matrix_h, cuda_dct_matrix_w, cuda_avg, d_out, cuda_Q)
    result = d_out.copy_to_host()
    end.record()
    end.synchronize()

    t_meas = cuda.event_elapsed_time(start, end) /1000

    cuda.defer_cleanup()  # Tell cuda to chill and clean VRAM
    return result, avg, t_setup, t_meas

