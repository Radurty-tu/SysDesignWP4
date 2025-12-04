import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm 
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"    # auto works in terminals and notebooks
'''
def plot_lug_cube(npz_path):
    # Load with memory mapping (no 4 GB copy)
    data = np.load(npz_path, mmap_mode='r')
    result = data["result"]   # shape (N, N, N, 4), memmapped

    N = result.shape[0]

    D_list, W_list, T_list, MS_list = [], [], [], []

    # Iterate over slices with a progress bar
    for i in tqdm(range(N), desc="Processing slices"):
        block = result[i]  # shape (N, N, 4)

        MS = block[..., 0]
        mask = MS > 0.0

        if mask.any():
            MS_list.append(MS[mask].ravel())
            D_list.append(block[..., 1][mask].ravel())
            W_list.append(block[..., 2][mask].ravel())
            T_list.append(block[..., 3][mask].ravel())

    # Concatenate to get exactly the same flattened arrays
    MS_flat = np.concatenate(MS_list)
    D_flat  = np.concatenate(D_list)
    W_flat  = np.concatenate(W_list)
    T_flat  = np.concatenate(T_list)

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    sc = ax.scatter(
        D_flat, W_flat, T_flat,
        c=MS_flat,
        cmap="viridis",
        s=8,
        alpha=0.7,
        linewidths=0
    )

    ax.set_xlabel("D [m]")
    ax.set_ylabel("W [m]")
    ax.set_zlabel("T [m]")
    ax.set_title("Lug design cube: MS > 0")

    cbar = fig.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label("Margin of Safety")

    plt.tight_layout()
    plt.show()

'''
import plotly.express as px

def plot_lug_cube(npz_path):
    data = np.load(npz_path, mmap_mode='r')
    result = data["result"]
    N = result.shape[0]

    D_list, W_list, T_list, MS_list = [], [], [], []

    for i in range(N):
        block = result[i]
        MS = block[..., 0]
        mask = MS > 0.0
        if mask.any():
            MS_list.append(MS[mask].ravel())
            D_list.append(block[..., 1][mask].ravel())
            W_list.append(block[..., 2][mask].ravel())
            T_list.append(block[..., 3][mask].ravel())

    MS_flat = np.concatenate(MS_list)
    D_flat  = np.concatenate(D_list)
    W_flat  = np.concatenate(W_list)
    T_flat  = np.concatenate(T_list)

    fig = px.scatter_3d(
        x=D_flat,
        y=W_flat,
        z=T_flat,
        color=MS_flat,
        labels={"x":"D [m]","y":"W [m]","z":"T [m]","color":"MS"},
        title="Lug design cube: MS > 0"
    )
    fig.update_traces(marker=dict(size=3, opacity=0.7))
    fig.show()





# >>> This is the part that was missing before <<<


plot_lug_cube("../Data/lug_scan.npz")
