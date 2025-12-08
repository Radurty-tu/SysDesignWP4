import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pio.renderers.default = "browser"  # or keep whatever you already set


def plot_MS_spaces_plotly(
    lug_npz="./Data/lug_scan.npz",
    fb_npz="./Data/fastener_bearing_scan.npz",
    pt_npz="./Data/fastener_pullthrough_scan.npz",
    th_npz="./Data/fastener_thermal_bearing_scan_4_11.npz",
    MS_min_req=0.1,
    eps=1e-3,
):
    # ----------------- LUG SIDE -----------------
    lug = np.load(lug_npz)

    # Prefer the newer format if present
    if "MS" in lug.files and {"D_arr", "W_arr", "T_arr"}.issubset(lug.files):
        MS_lug = lug["MS"]                    # shape (nD, nW, nT)
        D_arr  = lug["D_arr"]
        W_arr  = lug["W_arr"]
        T_arr  = lug["T_arr"]

        Dg, Wg, Tg = np.meshgrid(D_arr, W_arr, T_arr, indexing="ij")
        D_flat  = Dg.ravel()
        W_flat  = Wg.ravel()
        T_flat  = Tg.ravel()
        MS_flat = MS_lug.ravel()

    else:
        # Fallback to your old "result" layout, like plot_lug_cube
        result = lug["result"]
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

        if not MS_list:
            print("No MS > 0 in lug_scan; nothing to plot.")
            return

        MS_flat = np.concatenate(MS_list)
        D_flat  = np.concatenate(D_list)
        W_flat  = np.concatenate(W_list)
        T_flat  = np.concatenate(T_list)

    # Apply safety mask
    lug_safe_mask = MS_flat >= MS_min_req
    if not np.any(lug_safe_mask):
        raise RuntimeError("no safe lug points")

    D_flat  = D_flat[lug_safe_mask]
    W_flat  = W_flat[lug_safe_mask]
    T_flat  = T_flat[lug_safe_mask]
    MS_lug_flat = MS_flat[lug_safe_mask]

    best_lug_MS = float(MS_lug_flat.min())

    # ----------------- FASTENER SIDE -----------------
    fb = np.load(fb_npz)
    D2_arr = fb["D2_arr"]
    t2_arr = fb["t2_arr"]

    pt = np.load(pt_npz)
    if not np.array_equal(D2_arr, pt["D2_arr"]):
        raise RuntimeError("D2 mismatch")
    if not np.array_equal(t2_arr, pt["t2_arr"]):
        raise RuntimeError("t2 mismatch")
    t3_arr = pt["t3_arr"]
    MS2 = pt["MS2"]
    MS3 = pt["MS3"]

    th = np.load(th_npz)
    if not np.array_equal(D2_arr, th["D2_arr"]):
        raise RuntimeError("D2 mismatch th")
    if not np.array_equal(t2_arr, th["t2_arr"]):
        raise RuntimeError("t2 mismatch th")
    if not np.array_equal(t3_arr, th["t3_arr"]):
        raise RuntimeError("t3 mismatch th")
    MS_clamped    = th["MS_clamped"]
    MS_spacecraft = th["MS_spacecraft"]

    MS_fast = np.minimum.reduce((MS2, MS3, MS_clamped, MS_spacecraft))  # (nD2, nt2, nt3)

    D2g, t2g, t3g = np.meshgrid(D2_arr, t2_arr, t3_arr, indexing="ij")
    D2_flat  = D2g.ravel()
    t2_flat  = t2g.ravel()
    t3_flat  = t3g.ravel()
    MS_f_flat = MS_fast.ravel()

    fast_safe_mask = MS_f_flat >= MS_min_req
    if not np.any(fast_safe_mask):
        raise RuntimeError("no safe fastener points")

    D2_flat   = D2_flat[fast_safe_mask]
    t2_flat   = t2_flat[fast_safe_mask]
    t3_flat   = t3_flat[fast_safe_mask]
    MS_fast_flat = MS_f_flat[fast_safe_mask]

    best_fast_MS = float(MS_fast_flat.min())

    # Global minimum according to your current definition
    best_MS = min(best_lug_MS, best_fast_MS)

    # Contour masks at "minimum MS"
    lug_contour_mask  = np.abs(MS_lug_flat  - best_MS) < eps
    fast_contour_mask = np.abs(MS_fast_flat - best_MS) < eps

    # ----------------- PLOTTING -----------------
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "scene"}, {"type": "scene"}]],
        subplot_titles=(
            f"Lug space (best_lug_MS={best_lug_MS:.3f}, global={best_MS:.3f})",
            f"Fastener space (best_fast_MS={best_fast_MS:.3f}, global={best_MS:.3f})",
        ),
    )

    # Left: lug space
    fig.add_trace(
        go.Scatter3d(
            x=D_flat,
            y=W_flat,
            z=T_flat,
            mode="markers",
            marker=dict(
                size=3,
                opacity=0.9,
                color=MS_lug_flat,
                colorscale="IceFire",
                colorbar=dict(title="MS_lug"),
            ),
            name="lug MS",
        ),
        row=1,
        col=1,
    )

    # Lug contour at global min MS
    if np.any(lug_contour_mask):
        fig.add_trace(
            go.Scatter3d(
                x=D_flat[lug_contour_mask],
                y=W_flat[lug_contour_mask],
                z=T_flat[lug_contour_mask],
                mode="markers",
                marker=dict(size=5, color="lime"),
                name=f"lug MS ≈ {best_MS:.3f}",
            ),
            row=1,
            col=1,
        )

    fig.update_scenes(
        xaxis_title="D1 [m]",
        yaxis_title="W [m]",
        zaxis_title="T1 [m]",
        row=1,
        col=1,
    )

    # Right: fastener space
    fig.add_trace(
        go.Scatter3d(
            x=D2_flat,
            y=t2_flat,
            z=t3_flat,
            mode="markers",
            marker=dict(
                size=3,
                opacity=0.9,
                color=MS_fast_flat,
                colorscale="IceFire",
                colorbar=dict(title="MS_fast"),
            ),
            name="fastener MS",
        ),
        row=1,
        col=2,
    )

    # Fastener contour at global min MS
    if np.any(fast_contour_mask):
        fig.add_trace(
            go.Scatter3d(
                x=D2_flat[fast_contour_mask],
                y=t2_flat[fast_contour_mask],
                z=t3_flat[fast_contour_mask],
                mode="markers",
                marker=dict(size=5, color="lime"),
                name=f"fast MS ≈ {best_MS:.3f}",
            ),
            row=1,
            col=2,
        )

    fig.update_scenes(
        xaxis_title="D2 [m]",
        yaxis_title="t2 [m]",
        zaxis_title="t3 [m]",
        row=1,
        col=2,
    )

    fig.update_layout(
        title=f"Lug and fastener design spaces (MS_min_req={MS_min_req}, global min MS={best_MS:.3f})",
        showlegend=True,
    )

    fig.show()
    return fig
plot_MS_spaces_plotly()