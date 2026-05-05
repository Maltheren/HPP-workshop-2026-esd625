import numpy as np
import pandas as pd
import Cuda_Compression
import Naive_Compression
import Numba_Compression
import Numpy_Compression
import Numba_P_Compression


Q = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68,109,103, 77],
    [24, 35, 55, 64, 81,104,113, 92],
    [49, 64, 78, 87,103,121,120,101],
    [72, 92, 95, 98,112,100,103, 99]
], dtype=np.float32)

block_h, block_w = 8, 8
RUNS = 30

# Billedstørrelser der ligner rigtige billeder
x = 128   # start
y = 8192*2  # slut

sizes = [(2**n, 2**n) for n in range(int(np.log2(x)), int(np.log2(y)) + 1)]
algorithms = {
    #"Naive":  Naive_Compression,
    #"Numpy":  Numpy_Compression,
    #"Numba":  Numba_Compression,
    #"CUDA":   Cuda_Compression,
    "Numba_multicore": Numba_P_Compression,
}

results = []

for (H, W) in sizes:
    print(f"\n=== Størrelse {H}x{W} ===")

    for alg_name, module in algorithms.items():
        print(f"  Kører {alg_name}...", end=" ", flush=True)

        setup_times = []
        meas_times  = []

        for run in range(RUNS):
            # Ny random matrice hver iteration
            img = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)

            try:
                _, _, t_setup, t_meas = module.compress(img, Q, block_h, block_w)
                setup_times.append(t_setup)
                meas_times.append(t_meas)
            except Exception as e:
                print(f"FEJL: {e}")
                break

        if meas_times:
            results.append({
                "Algorithm":    alg_name,
                "Size":         f"{H}x{W}",
                "Pixels":       H * W,
                "Setup_mean":   np.mean(setup_times),
                "Setup_std":    np.std(setup_times),
                "Compute_mean": np.mean(meas_times),
                "Compute_std":  np.std(meas_times),
                "Total_mean":   np.mean(np.array(setup_times) + np.array(meas_times)),
                "Min":          np.min(meas_times),
                "Max":          np.max(meas_times),
            })
            print(f"compute={np.mean(meas_times)*1000:.1f}ms ± {np.std(meas_times)*1000:.1f}ms")

df = pd.DataFrame(results)

# Pænt print
pd.set_option('display.float_format', lambda x: f'{x*1000:.2f}ms')
print("\n=== RESULTATER ===")
print(df[["Algorithm", "Size", "Compute_mean", "Compute_std", "Min", "Max"]].to_string(index=False))

# Gem til CSV
df.to_csv("benchmark_results_Numba_p_only.csv", index=False)
print("\nGemt til benchmark_results.csv")