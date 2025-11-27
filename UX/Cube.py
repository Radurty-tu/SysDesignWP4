import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # keeps some backends happy

def plot_lug_cube(npz_path):
    data = np.load(npz_path)
    result = data["result"]   # shape (N, N, N, 4): [MS, D, W, T]

    MS  = result[..., 0]
    D   = result[..., 1]
    W   = result[..., 2]
    T   = result[..., 3]

    # Mask: hide MS <= 0  (they will be "transparent")
    mask = MS > 0.0

    D_flat  = D[mask].ravel()
    W_flat  = W[mask].ravel()
    T_flat  = T[mask].ravel()
    MS_flat = MS[mask].ravel()

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    sc = ax.scatter(
        D_flat, W_flat, T_flat,
        c=MS_flat,
        cmap="viridis",
        s=8,
        alpha=0.7,    # semi transparent points
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

plot_lug_cube("../Data/lug_scan.npz")