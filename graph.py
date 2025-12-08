import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def plot_MS_spaces(ms_min_req=0.1, highlight_eps=1e-3):
    # Load lug data
    lug = np.load("./Data/lug_scan.npz")
    D1_arr = lug["D_arr"]
    W_arr  = lug["W_arr"]
    t1_arr = lug["T_arr"]
    if "MS" in lug.files:
        MS_lug = lug["MS"]              # shape (nD1, nW, nt1)
    else:
        MS_lug = lug["result"][..., 0]

    # Load fastener data
    fb = np.load("./Data/fastener_bearing_scan.npz")
    D2_arr = fb["D2_arr"]
    t2_arr = fb["t2_arr"]

    pt = np.load("./Data/fastener_pullthrough_scan.npz")
    if not np.array_equal(D2_arr, pt["D2_arr"]):
        raise RuntimeError("D2 mismatch")
    if not np.array_equal(t2_arr, pt["t2_arr"]):
        raise RuntimeError("t2 mismatch")
    t3_arr = pt["t3_arr"]
    MS2 = pt["MS2"]
    MS3 = pt["MS3"]

    th = np.load("./Data/fastener_thermal_bearing_scan_4_11.npz")
    if not np.array_equal(D2_arr, th["D2_arr"]):
        raise RuntimeError("D2 mismatch th")
    if not np.array_equal(t2_arr, th["t2_arr"]):
        raise RuntimeError("t2 mismatch th")
    if not np.array_equal(t3_arr, th["t3_arr"]):
        raise RuntimeError("t3 mismatch th")
    MS_clamped     = th["MS_clamped"]
    MS_spacecraft  = th["MS_spacecraft"]

    MS_fast = np.minimum.reduce((MS2, MS3, MS_clamped, MS_spacecraft))  # (nD2, nt2, nt3)

    # Safe masks
    safe_lug_mask  = MS_lug  >= ms_min_req
    safe_fast_mask = MS_fast >= ms_min_req
    if not np.any(safe_lug_mask):
        raise RuntimeError("no safe lug points")
    if not np.any(safe_fast_mask):
        raise RuntimeError("no safe fastener points")

    # Current definition of minima, same as in your run()
    best_lug_MS  = float(MS_lug[safe_lug_mask].min())
    best_fast_MS = float(MS_fast[safe_fast_mask].min())
    best_MS      = min(best_lug_MS, best_fast_MS)

    # Coordinate grids
    D1g, Wg, t1g   = np.meshgrid(D1_arr, W_arr, t1_arr,  indexing="ij")
    D2g, t2g, t3g  = np.meshgrid(D2_arr, t2_arr, t3_arr, indexing="ij")

    # Keep only safe points
    D1p  = D1g[safe_lug_mask]
    Wp   = Wg[safe_lug_mask]
    t1p  = t1g[safe_lug_mask]
    MSlp = MS_lug[safe_lug_mask]

    D2p  = D2g[safe_fast_mask]
    t2p  = t2g[safe_fast_mask]
    t3p  = t3g[safe_fast_mask]
    MSfp = MS_fast[safe_fast_mask]

    # Contour of "minimum MS" according to your current definition
    lug_contour_mask  = np.abs(MSlp - best_MS) < highlight_eps
    fast_contour_mask = np.abs(MSfp - best_MS) < highlight_eps

    fig = plt.figure(figsize=(10, 4))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    # Left: lug space, colored by MS_lug, green for contour at best_MS
    sc1 = ax1.scatter(D1p, Wp, t1p, c=MSlp, s=10)
    fig.colorbar(sc1, ax=ax1, label="MS_lug")
    ax1.scatter(D1p[lug_contour_mask], Wp[lug_contour_mask], t1p[lug_contour_mask],
                c="g", s=30)
    ax1.set_xlabel("D1")
    ax1.set_ylabel("W")
    ax1.set_zlabel("t1")
    ax1.set_title(f"Lug space  best_lug_MS={best_lug_MS:.3f}  global_min={best_MS:.3f}")

    # Right: fastener space, colored by MS_fast, green for contour at best_MS
    sc2 = ax2.scatter(D2p, t2p, t3p, c=MSfp, s=10)
    fig.colorbar(sc2, ax=ax2, label="MS_fast")
    ax2.scatter(D2p[fast_contour_mask], t2p[fast_contour_mask], t3p[fast_contour_mask],
                c="g", s=30)
    ax2.set_xlabel("D2")
    ax2.set_ylabel("t2")
    ax2.set_zlabel("t3")
    ax2.set_title(f"Fastener space  best_fast_MS={best_fast_MS:.3f}  global_min={best_MS:.3f}")

    plt.tight_layout()
    plt.show()
    
plot_MS_spaces()
