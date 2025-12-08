'''
black box diagram
blood sweat and tears (ykw)

Loads
Fx,Fz (in plane)
My?

Geometry
xi,zi
D2 t2

Material
sigma_br_allow

Outputs:
Pi[i] in plane load
sigma_br[i] stress at each
Ms_br[i] margin at each
ms_br_min minimum margin

'''
import numpy as np
import math

def p4check(X_list,Z_list,D2):
    X=np.asarray(X_list,dtype=float)
    Z=np.asarray(Z_list,dtype=float)
    if X.shape != Z.shape or X.ndim != 1:
        raise RuntimeError("p4check: X and Z must be 1D arrays of same length")
    
    n=X.size
    if n == 0:
        raise RuntimeError("p4check: empty fastener list")
    
    min_space=2
    min_edge=1.5
    #fastner distance
    coords = np.stack((X, Z), axis=-1)
    diff = coords[:, None, :] - coords[None, :, :]  # (n, n, 2)
    dist = np.linalg.norm(diff, axis=-1)      # (n, n)
    iu, ju = np.triu_indices(n, k=1)
    d_pairs = dist[iu, ju]
    spacingD = d_pairs / D2
    min_spacingD=float(np.min(spacingD))
    if min_spacingD < min_space:
        return 0,0
    
    
    #edge distance
    #we do not have a plate
    #as such we create the minimum plate size for our purposes.
    e_min = min_edge * D2
    x_min=float(np.min(X))
    x_max=float(np.max(X))
    z_min=float(np.min(Z))
    z_max=float(np.max(Z))
    span_x = x_max - x_min
    span_z = z_max - z_min
    width_min  = span_x + 2.0 * e_min
    height_min = span_z + 2.0 * e_min
    return width_min,height_min #this creates the minimum plate size
#height min is w from 4.3, we will use it to truncate the lug scan later.



def run(config,geometry,loads):
    FX=loads["FX"]
    FZ=loads["FZ"]
    MY=loads["MY"]
    
    X_list=geometry["X_list"]
    Z_list=geometry["Z_list"]
    D2_min=geometry["D2_min"]
    D2_max=geometry["D2_max"]
    t2_min=geometry["t2_min"]
    t2_max=geometry["t2_max"]
    N=geometry["N"]
    
    sigma_allow=config["sigma_br_allow"]
    tol=config["bearing_zero_tolerance"]
    X = np.asarray(X_list, dtype=float)
    Z = np.asarray(Z_list, dtype=float)
    
    xcg = X.mean()
    zcg = Z.mean()
    if abs(xcg) > tol or abs(zcg) > tol:
        raise RuntimeError(
            f"4.5 centroid must be at origin: got xcg={xcg:.6e}, zcg={zcg:.6e}"
        )
    #4.5 done
    
    
    R=np.sqrt(X*X+Z*Z)
    R2=np.sum(R**2)
    n=X.size
    FXi=np.full(n,FX/n)
    FZi=np.full(n,FZ/n)
    FMi=MY*R/R2
    FxMi = np.zeros_like(FMi)
    FzMi = np.zeros_like(FMi)

    mask = R > 0.0
    FxMi[mask] = -FMi[mask] * Z[mask] / R[mask]
    FzMi[mask] =  FMi[mask] * X[mask] / R[mask]
    
    FXi=FXi+FxMi
    FZi=FZi+FzMi
    Pi=np.sqrt(FXi**2 + FZi**2) #FZi!! Freddy fazbear, har har har har
    #end of 4.6
    
    D2_arr = np.linspace(D2_min, D2_max, N)
    t2_arr = np.linspace(t2_min, t2_max, N)
    
    # height_min will be used as "w" (z-direction), width_min as "L" (x-direction)
    w_min_arr = np.zeros_like(D2_arr)  # height
    L_min_arr = np.zeros_like(D2_arr)  # width
    valid_D2  = np.ones_like(D2_arr, dtype=bool)
    
    for i, D2 in enumerate(D2_arr):
        #can afford a for here, O(N)
        width_min, height_min = p4check(X_list, Z_list, D2)
        L_min_arr[i] = width_min
        w_min_arr[i] = height_min
        if width_min <= 0.0 or height_min <= 0.0:
            valid_D2[i] = False
    D2_grid, t2_grid = np.meshgrid(D2_arr, t2_arr, indexing="ij")
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = D2_grid[None, :, :] * t2_grid[None, :, :]      # (1,N,N)
        sigma_br = Pi[:, None, None] / denom                   # (n,N,N)
        MS = sigma_allow / sigma_br - 1.0                      # (n,N,N)
    MS_min_grid = np.min(MS, axis=0)
    output_path = "../Data/fastener_bearing_scan.npz"
    np.savez(
    output_path,
    D2_arr=D2_arr,
    t2_arr=t2_arr,
    MS_min_grid=MS_min_grid,
    w_min=w_min_arr,
    L_min=L_min_arr,
    )
    return output_path
    