
import numpy as np
from PIL import Image
from numba import jit
from numpy import asarray
from multiprocessing import Pool, cpu_count
from numba import cuda, float32






# Lav IDCT matrix
def create_idct_matrix(N):
    C = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for n in range(N):
            if n == 0:
                C[i, n] = 1.0 / N
            else:
                C[i, n] = (2.0 / N) * np.cos(np.pi * n * (2*i + 1) / (2*N))
    return C

def create_dct_matrix(N):
    C = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for n in range(N):
            C[i, n] = np.cos(np.pi * i * (2*n + 1) / (2*N))
    return C

def create_dct_matrices(H, W):
    C_h = create_dct_matrix(H)
    C_w = create_dct_matrix(W)
    return C_h, C_w



def pad_and_partition_hw(image: np.ndarray, h_out: int, w_out: int) -> list[list[list[np.ndarray]], float]:
    h, w = image.shape[:2]

    pad_h = (h_out - h % h_out) % h_out
    pad_w = (w_out - w % w_out) % w_out

    if image.ndim == 2:
        padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='edge')
    else:
        padded = np.pad(image, ((0, pad_h), (0, pad_w), (0, 0)), mode='edge')

    H, W = padded.shape[:2]

    n_h = H // h_out
    n_w = W // w_out

    # Creating a 2d array
    blocks = [
        [
            padded[i*h_out:(i+1)*h_out, j*w_out:(j+1)*w_out]
            for j in range(n_w)
        ]
        for i in range(n_h)
    ]

    avg = padded.mean(axis=2).mean() if padded.ndim == 3 else padded.mean()

    return blocks, avg







def reconstruct_from_blocks(blocks_np):
    """
    Samler partitions tilbage til et billede.
    blocks_np shape: (n_h, n_w, block_h, block_w, 3) eller (n_h, n_w, block_h, block_w)
    """
    n_h, n_w, block_h, block_w = blocks_np.shape[:4]
    
    if blocks_np.ndim == 5:
        # RGB
        img = np.zeros((n_h * block_h, n_w * block_w, 3), dtype=np.uint8)
        for i in range(n_h):
            for j in range(n_w):
                img[i*block_h:(i+1)*block_h, j*block_w:(j+1)*block_w] = blocks_np[i, j].astype(np.uint8)
    else:
        # Grayscale (f.eks. efter DCT output)
        img = np.zeros((n_h * block_h, n_w * block_w), dtype=np.float32)
        for i in range(n_h):
            for j in range(n_w):
                img[i*block_h:(i+1)*block_h, j*block_w:(j+1)*block_w] = blocks_np[i, j]
        # Normaliser til 0-255 så PIL kan vise det
        img = img - img.min()
        img = (img / img.max() * 255).astype(np.uint8)

    return Image.fromarray(img)

def matprint(mat, fmt="g"):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  ")
        print("")
  

if __name__ == "__main__":

    # Tag en enkelt blok fra midten
    mid_h = result.shape[0] // 2
    mid_w = result.shape[1] // 2

    # Original blok som grayscale + centreret
    original_block = blocks_np[mid_h, mid_w, :, :, :].mean(axis=2) - avg

    # Scipy DCT på samme blok
    scipy_dct = dct(dct(original_block, axis=0), axis=1)

    # Din CUDA DCT på samme blok  
    cuda_dct = result[mid_h, mid_w]

    print("Scipy DCT [0,0]:", scipy_dct[0,0])
    print("CUDA DCT  [0,0]:", cuda_dct[0,0])
    print("Ratio:", scipy_dct[0,0] / cuda_dct[0,0])

    print("\nScipy DCT første række:", scipy_dct[0,:])
    print("CUDA DCT første række: ", cuda_dct[0,:])

    print("\nScipy DCT første kolonne:", scipy_dct[:,0])
    print("CUDA DCT første kolonne: ", cuda_dct[:,0])