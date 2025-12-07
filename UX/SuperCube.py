import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.colors import hsv_to_rgb

# FORCE PLOTLY TO OPEN YOUR WEB BROWSER
pio.renderers.default = "browser"


def plot_6d_cube(npz_path):
    data = np.load(npz_path, mmap_mode="r")
    result = data["result"]          # assume shape (N, ..., 6)
    N = result.shape[0]

    D1_list, t1_list, w_list = [], [], []
    t2_list, D2_list, mass_list = [], [], []

    # Example mask: keep only points with mass > 0
    for i in range(N):
        block = result[i]
        mass = block[..., 5]
        mask = mass > 0.0

        if mask.any():
            D1_list.append(block[..., 0][mask].ravel())
            t1_list.append(block[..., 1][mask].ravel())
            w_list.append(block[..., 2][mask].ravel())
            t2_list.append(block[..., 3][mask].ravel())
            D2_list.append(block[..., 4][mask].ravel())
            mass_list.append(mass[mask].ravel())

    if not D1_list:
        print("No valid points; nothing to plot.")
        return

    D1   = np.concatenate(D1_list)
    t1   = np.concatenate(t1_list)
    w    = np.concatenate(w_list)
    t2   = np.concatenate(t2_list)
    D2   = np.concatenate(D2_list)
    mass = np.concatenate(mass_list)

    # ---------- normalize ----------
    def norm01(x):
        x_min = x.min()
        x_ptp = np.ptp(x)   # NumPy 2.0 fix
        if x_ptp == 0:
            return np.zeros_like(x)
        return (x - x_min) / x_ptp

    H = norm01(t1)
    S = norm01(t2)
    V = norm01(mass)

    hsv = np.column_stack([H, S, V])
    rgb = (hsv_to_rgb(hsv) * 255).astype(int)
    rgb_strings = [f"rgb({r},{g},{b})" for r, g, b in rgb]

    # ---------- PLOT ----------
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=D1,
                y=w,
                z=D2,
                mode="markers",
                marker=dict(
                    size=3,
                    color=rgb_strings,
                    opacity=1.0
                ),
            )
        ]
    )

    fig.update_layout(
        title="Design cube: (D1, w, D2) with HSV(t1, t2, mass)",
        scene=dict(
            xaxis_title="D1",
            yaxis_title="w",
            zaxis_title="D2",
        )
    )

    # THIS WILL OPEN THE BROWSER
    fig.show()


# test
plot_6d_cube("../Data/lug_scan_placeholder_6d.npz")
