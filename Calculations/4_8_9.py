'''
Black box diagram
same as previous one but for out of plane. quite simple really

    
'''

#Fpi=Fy/nf
#FpMz=Mz*Ai*ri/sigma (Airi**2)

import numpy as np
import matplotlib.pyplot as plt
def run(loads,geometry,config):
    FY=loads["FY"]
    MZ=loads["MZ"]
    X_list=geometry["X_list"]
    Z_list=geometry["Z_list"]
    t2_min=geometry["t2_min"]
    t2_max=geometry["t2_max"]
    t3_min=geometry["t3_min"]
    t3_max=geometry["t3_max"]
    N=geometry["N"]
    Dfi=geometry["Dfi"]
    
    tau2_allow=5
    tau3_allow=5
    
    X = np.asarray(geometry["X_list"], dtype=float)
    Z = np.asarray(geometry["Z_list"], dtype=float)
    n = X.size
    R=np.sqrt(X**2+Z**2)
    FPy= np.full(n,FY/n)
    FpMz = np.zeros(n)
    R2=np.sum(R**2) #technically wasting compute here but let's be real
    sign_z = np.sign(Z)
    FpMz=MZ*R/R2*sign_z
    FPTy=FPy+FpMz
    #end of 4.8
    
    
    t2_arr = np.linspace(t2_min, t2_max, N)
    t3_arr = np.linspace(t3_min, t3_max, N)
    t2_grid, t3_grid = np.meshgrid(t2_arr, t3_arr, indexing="ij")  # (N,N)
    A2 = np.pi*Dfi*t2_grid
    A3 = np.pi*Dfi*t3_grid
    FPTy_3d = FPTy[:,None,None]
    with np.errstate(divide="ignore", invalid="ignore"):
        tau2 = FPTy_3d / A2[None, :, :]   # (nf,N,N)
        tau3 = FPTy_3d / A3[None, :, :]   # (nf,N,N)
    
    tau2_abs = np.abs(tau2)
    tau3_abs = np.abs(tau3)
    
    tau2_abs = np.abs(tau2)
    tau3_abs = np.abs(tau3)
    
    MS2 = tau2_allow / tau2_abs - 1.0
    MS3 = tau3_allow / tau3_abs - 1.0
    MS2_min_grid = np.min(MS2, axis=0)    # (N,N)
    MS3_min_grid = np.min(MS3, axis=0)    # (N,N)
    
    output_path = "../Data/fastener_pullthrough_scan.npz"
    np.savez(
        output_path,
        t2_arr=t2_arr,
        t3_arr=t3_arr,
        MS2_min_grid=MS2_min_grid,
        MS3_min_grid=MS3_min_grid,
    )

    return output_path