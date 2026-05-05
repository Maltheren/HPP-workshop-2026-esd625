import numpy as np
from PIL import Image
from numpy import asarray
import Inverse_compression
from numba import cuda
import Cuda_Compression
import Naive_Compression
import Numba_Compression
import Numpy_Compression


if __name__ == "__main__":
    img = Image.open('./images/Mikkel1.jpg')
    img = img.convert('RGB')
    img = asarray(img)
    Q = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68,109,103, 77],
        [24, 35, 55, 64, 81,104,113, 92],
        [49, 64, 78, 87,103,121,120,101],
        [72, 92, 95, 98,112,100,103, 99]
    ])
    Q *= 100
    block_h, block_w = 8, 8

    ##Warm up

    result, avg, t_setup, t_meas = Numpy_Compression.compress(img, Q, block_h, block_w)


    # Hvad er der faktisk i dit output?
    print(f"timespan: {t_setup},\t {t_meas}")
    print("Min:", result.min())
    print("Max:", result.max())
    print("Mean:", result.mean())
    print("Std:", result.std())  # Er der overhovedet variation?
    reconstructed_img = Inverse_compression.decompress(result, Q, avg, block_h, block_w)

    reconstructed_img.save("reconstructed4.png")

    
