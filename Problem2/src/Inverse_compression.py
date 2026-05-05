import numpy as np
from PIL import Image
from converters import create_dct_matrix, create_idct_matrix, create_dct_matrices

def decompress(quantized, Q, avg, block_h, block_w):
    """
    quantized: np array med shape (n_h, n_w, block_h, block_w)
    Q: kvantiseringsmatrix (8x8)
    avg: den gennemsnitlige værdi der blev trukket fra ved komprimering
    """
    n_h, n_w = quantized.shape[:2]
    

    
    C_h = create_idct_matrix(block_h)
    C_w = create_idct_matrix(block_w)
    
    # Output billede
    img = np.zeros((n_h * block_h, n_w * block_w), dtype=np.float32)

    
    for bi in range(n_h):
        for bj in range(n_w):
            block = quantized[bi, bj].astype(np.float32)
            
            # 1. De-kvantisering
            dequant = block * Q
            
            # 2. IDCT på rækker
            temp = np.zeros((block_h, block_w), dtype=np.float32)
            for i in range(block_h):
                for j in range(block_w):
                    temp[i, j] = np.dot(C_h[i, :], dequant[:, j])
            
            # 3. IDCT på kolonner
            reconstructed = np.zeros((block_h, block_w), dtype=np.float32)
            for i in range(block_h):
                for j in range(block_w):
                    reconstructed[i, j] = np.dot(temp[i, :], C_w[j, :])


            # 4. Tilføj gennemsnittet tilbage
            reconstructed += avg
            

            # Sæt blokken ind i billedet
            img[bi*block_h:(bi+1)*block_h, bj*block_w:(bj+1)*block_w] = reconstructed


    print("Før clip - Min:", img.min(), "Max:", img.max())
    # Clip til 0-255 og konverter til billede
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, mode='L')  # L = grayscale
    