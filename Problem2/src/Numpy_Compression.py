import numpy as np
from converters import pad_and_partition_hw, create_dct_matrices
import time



import numpy as np
from converters import pad_and_partition_hw, create_dct_matrices
import time


##Mest kradsbørstige Numpy streamlining af systemet
def compress(img, Q, block_h, block_w):
    t_0 = time.perf_counter()
    blocks, avg = pad_and_partition_hw(img, block_h, block_w)
    blocks_np = np.array(blocks, dtype=np.float32)
    dct_h, dct_w = create_dct_matrices(8, 8)
    t_1 = time.perf_counter()
    t_setup = t_1 - t_0

    t_0 = time.perf_counter()

    # 1. Grayscale + center - alle blokke på én gang
    # blocks_np shape: (n_h, n_w, 8, 8, 3)
    gray = blocks_np.mean(axis=4) - avg  # (n_h, n_w, 8, 8)

    # 2. Row DCT: dct_h @ block for alle blokke på én gang
    # einsum: for hver blok, gang dct_h[i,k] * gray[k,j] -> temp[i,j]
    temp = np.einsum('ik,hwkj->hwij', dct_h, gray)

    # 3. Col DCT: temp @ dct_w^T for alle blokke på én gang
    dct_out = np.einsum('hwik,jk->hwij', temp, dct_w)

    # 4. Kvantisering
    out = np.round(dct_out / Q).astype(np.float32)

    t_1 = time.perf_counter()
    t_meas = t_1 - t_0

    return out, avg, t_setup, t_meas