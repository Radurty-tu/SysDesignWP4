import numpy as np

def run(config,geometry,loads):
    MS_min_req=0.1

    lug=np.load("./Data/lug_scan.npz")
    D1_arr=lug["D_arr"]
    W_arr=lug["W_arr"]
    t1_arr=lug["T_arr"]
    if "MS" in lug.files:
        MS_lug=lug["MS"]
    else:
        MS_lug=lug["result"][...,0]

    fb=np.load("./Data/fastener_bearing_scan.npz")
    D2_arr=fb["D2_arr"]
    t2_arr=fb["t2_arr"]

    pt=np.load("./Data/fastener_pullthrough_scan.npz")
    if not np.array_equal(D2_arr,pt["D2_arr"]):raise RuntimeError("D2 mismatch")
    if not np.array_equal(t2_arr,pt["t2_arr"]):raise RuntimeError("t2 mismatch")
    t3_arr=pt["t3_arr"]
    MS2=pt["MS2"]
    MS3=pt["MS3"]

    th=np.load("./Data/fastener_thermal_bearing_scan_4_11.npz")
    if not np.array_equal(D2_arr,th["D2_arr"]):raise RuntimeError("D2 mismatch th")
    if not np.array_equal(t2_arr,th["t2_arr"]):raise RuntimeError("t2 mismatch th")
    if not np.array_equal(t3_arr,th["t3_arr"]):raise RuntimeError("t3 mismatch th")
    MS_clamped=th["MS_clamped"]
    MS_spacecraft=th["MS_spacecraft"]

    MS_fast=np.minimum.reduce((MS2,MS3,MS_clamped,MS_spacecraft))

    safe_lug_mask=MS_lug>=MS_min_req
    safe_fast_mask=MS_fast>=MS_min_req
    if not np.any(safe_lug_mask):raise RuntimeError("no safe lug points")
    if not np.any(safe_fast_mask):raise RuntimeError("no safe fastener points")

    best_lug_MS=float(MS_lug[safe_lug_mask].min())
    best_fast_MS=float(MS_fast[safe_fast_mask].min())
    best_MS=min(best_lug_MS,best_fast_MS)
    eps=1e-9

    if best_lug_MS<=best_fast_MS+eps:
        lug_idx=np.argwhere(safe_lug_mask & (np.abs(MS_lug-best_lug_MS)<=eps))[0]
        fast_idx=np.argwhere(safe_fast_mask & (MS_fast>=best_MS-eps))[0]
    else:
        fast_idx=np.argwhere(safe_fast_mask & (np.abs(MS_fast-best_fast_MS)<=eps))[0]
        lug_idx=np.argwhere(safe_lug_mask & (MS_lug>=best_MS-eps))[0]

    i1,j1,k1=lug_idx
    i2,j2,k2=fast_idx

    D1_best=float(D1_arr[i1])
    W_best=float(W_arr[j1])
    t1_best=float(t1_arr[k1])
    D2_best=float(D2_arr[i2])
    t2_best=float(t2_arr[j2])
    t3_best=float(t3_arr[k2])

    best_lug_params=np.array([D1_best,W_best,t1_best])
    best_fast_params=np.array([D2_best,t2_best,t3_best])

    out="./Data/final_MS_summary.npz"
    np.savez(out,
        MS_min_req=MS_min_req,
        best_MS=best_MS,
        best_lug_MS=best_lug_MS,
        best_fast_MS=best_fast_MS,
        best_lug_params=best_lug_params,
        best_fast_params=best_fast_params,
        D1_arr=D1_arr,
        W_arr=W_arr,
        t1_arr=t1_arr,
        D2_arr=D2_arr,
        t2_arr=t2_arr,
        t3_arr=t3_arr)

    msg=(f"best_MS={best_MS:.3f}, "
         f"D1={D1_best:.4f}, W={W_best:.4f}, t1={t1_best:.4f}, "
         f"D2={D2_best:.4f}, t2={t2_best:.4f}, t3={t3_best:.4f}")
    return msg