import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm 
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"    # auto works in terminals and notebooks

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
        color_continuous_scale="IceFire",
        labels={"x":"D [m]","y":"W [m]","z":"T [m]","color":"MS"},
        title="Lug design cube: MS > 0"
    )
    fig.update_traces(marker=dict(size=3, opacity=1))
    fig.show()





# >>> This is the part that was missing before <<<


plot_lug_cube("../Data/lug_scan.npz")
