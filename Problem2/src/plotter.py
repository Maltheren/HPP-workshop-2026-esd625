import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scienceplots


if __name__ == "__main__":
    df1 = pd.read_csv("results/benchmark_results.csv")  
    df2 = pd.read_csv("results/benchmark_results_large.csv")
    df3 = pd.read_csv("results/benchmark_results_Stripped.csv")
    df4 = pd.read_csv("results/benchmark_results_Numba_p_only.csv")

    df_combined = pd.concat([df1, df2, df3, df4], ignore_index=True)
    df_combined["Size"] = df_combined["Size"].str.split("x").str[0].astype(int)

    plt.style.use(["science", "ieee"])
    fig, ax = plt.subplots(figsize=(8, 6))  # make it bigger

    sns.lineplot(data=df_combined, x="Size", y="Compute_mean", hue="Algorithm")

    # Log scales
    ax.set_yscale("log")

    # Main grid
    ax.grid(True)
    
    # Minor ticks + dotted subgrid
    ax.minorticks_on()
    ax.grid(which="major", linestyle="-", alpha=0.7)
    ax.grid(which="minor", linestyle=":", alpha=0.5)
    ax.set_xlabel("size [px * px]")
    ax.set_ylabel("Mean execution time [s]")
    # Save high-res
    plt.savefig("plot.pdf", bbox_inches="tight")