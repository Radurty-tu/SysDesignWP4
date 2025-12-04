'''
Black box diagram

Inputs:
    4.1- FX FY FZ F1 MX
    4.2- CONSTANT-DOUBLE LUG
    CONFIG-MATERIAL PROPERTIES, SAFETY FACTOR, MISALIGNMENTS

Outputs:
    D1-HOLE DIAMETER
    W-LUG WIDTH
    T1-LUG THICKNESS AT HOLE
    VERIFICATION
'''
import numpy as np
import math
import json
import k_value_calculate as k

def area(D,W,T):
    At=T*(W-D)
    Abr=T*(W-D)/2
    return At, Abr

def run(geometry,loads,config):
    '''
    PLAN:
        GET RANGES FOR DIAMETER, WIDTH, THICKNESS
        GET FINENESS
        GET LOADS
        GET CONFIG
        
        FOR EACH COMBINATION OF PARAMETERS (BASED ON FINENESS)
        VERIFY REQUIREMENTS
        IF REQUIREMENTS ARE NOT MET-SAVE AS 0
        IF REQUIREMENTS ARE MET SAVE AS (Mass? SF? Both? probably both)
        
    '''
    D_min = geometry["D_min"]
    D_max = geometry["D_max"]
    W_min = geometry["W_min"]
    W_max = geometry["W_max"]
    T_min = geometry["T_min"]
    T_max = geometry["T_max"]
    N  = geometry["N"]
    
    FX = loads["FX"]
    FY = loads["FY"]
    FZ = loads["FZ"]
    F1 = loads["F1"]
    MX = loads["MX"]
    
    FTU= config["FTU"]
    #KT=config["KT"]
    #KBR=config["KBR"]
    #KTU=config["KTU"]
    Mat=config["Material"]
    
    #Numpy section
    D_arr = np.linspace(D_min, D_max, N)
    W_arr = np.linspace(W_min, W_max, N)
    T_arr = np.linspace(T_min, T_max, N)
    
    
    
    D_grid, W_grid, T_grid = np.meshgrid(D_arr, W_arr, T_arr, indexing="ij")
    At_grid, Abr_grid = area(D_grid, W_grid, T_grid)
    geom_ok = W_grid > D_grid
    e_grid = 0.5 * (W_grid - D_grid)
    A_av_grid = (W_grid - D_grid) / T_grid
    
    
    CY= 0.6373*(T_grid/D_grid)- 0.3019
    ZY= 20.332*(T_grid/D_grid**2) + 8.3023*(T_grid/D_grid) + 0.5995
    KBRY_grid = (2/7) * ZY * (4 + CY) * (e_grid/D_grid - 0.5)/(e_grid/D_grid + CY)
    
    CU= -0.0004*(D_grid/T_grid**3) + 0.0283*(D_grid/T_grid**2)- 0.5444*(D_grid/T_grid) + 2.8731
    ZU=  0.0026*(D_grid/T_grid**2)- 0.1488*(D_grid/T_grid) + 2.5401
    KBRU_grid = ( ZU*(D_grid/T_grid)*(2.4 + CU)*(e_grid/D_grid - 0.5)/(e_grid/D_grid + CU) )/1.9
    
    
    K_ty_grid = k.compute_K_ty(A_av_grid)
    K_tu_grid = k.compute_K_tu(A_av_grid, Mat)

    Pu_grid   = K_ty_grid * FTU * At_grid
    Pbru_grid = KBRU_grid * FTU * Abr_grid
    P_ult_grid = np.minimum(Pu_grid, Pbru_grid)
    Ptu_grid = K_tu_grid * FTU * Abr_grid   
    Ra_grid = (FY + F1) / (P_ult_grid * 2.0)
    Rtr_grid = np.sqrt(FZ**2 + FX**2)/(Ptu_grid)/2
    Metric_grid = Ra_grid**1.6 + Rtr_grid**1.6
    MS_grid = np.zeros_like(Metric_grid)
    safe_mask = (Metric_grid < 1.0) & geom_ok
    MS_grid[safe_mask] = 1.0 / (Metric_grid[safe_mask]**0.625) - 1.0
    RESULT_grid = np.stack((MS_grid, D_grid, W_grid, T_grid), axis=-1)
    
    
    #save
    
    output_path = "../Data/lug_scan.npz"

    np.savez(output_path,
            result=RESULT_grid,
            D_arr=D_arr,
            W_arr=W_arr,
            T_arr=T_arr)



# we have R_a^1.6+R_tr^1.6 <1 for not failure
#Calculate ultimate axial load
#calculate ultimate transverse load
#use the stupid equation where R=(P/PU)
#the ultimate loads are fucked
#output safety factor MS= 1/(sum)
    
    #Pu=Kt*Ftu*At -> Ftu based on material, At geometry, Kt
    #Pbru=Kbru*Ftu*Abr
    
    
    
    return output_path


def plot(file, ax):
    data = np.load(file)
    result = data["result"]   # shape (N, N, N, 4)
    D_arr = data["D_arr"]
    W_arr = data["W_arr"]
    T_arr = data["T_arr"]
    MS = result[..., 0]       # MS field

    # Mid indices for W and T when plotting vs D
    j_mid = len(W_arr) // 2
    k_mid = len(T_arr) // 2

    MS_vs_D = MS[:, j_mid, k_mid]

    ax.clear()
    ax.plot(D_arr, MS_vs_D)
    ax.set_xlabel("D [m]")
    ax.set_ylabel("Margin of Safety")
    ax.set_title("MS vs D (W, T at mid)")
    ax.grid(True)


if __name__ == "__main__":
    
    # Geometry sweep ranges
    geometry = {
        "D_min": 0.005,   # 5 mm
        "D_max": 0.020,   # 20 mm
        "W_min": 0.010,   # 10 mm
        "W_max": 0.040,   # 40 mm
        "T_min": 0.002,   # 2 mm
        "T_max": 0.010,   # 10 mm
        "N": 100           # fineness of grid
    }
    
    # Loads (edit to match WP4)
    loads = {
        "FX": 100.0,
        "FY": 500.0,
        "FZ": 200.0,
        "F1": 0.0,
        "MX": 0.0
    }
    #e/d=Kbr+0.5
    #
    # Material and configuration parameters
    config = {
        "FTU": 400e6,   # tensile strength (Pa)
        "KT": 0.4,      # axial factor
        "KBR": 1,     # bearing factor
        "KTU": 0.4,      # transverse factor
        "Material":1
    }

    # Call the design function
    run(geometry, loads, config)
    
    print("Lug sweep completed. Data saved to ../Data/lug_scan.npz")
    # Find and show max MS and its geometry
    data = np.load("../Data/lug_scan.npz")
    result = data["result"]                 # shape (N, N, N, 4)
    MS = result[..., 0]                    # MS field
    i, j, k = np.unravel_index(np.argmax(MS), MS.shape)
    best_MS = MS[i, j, k]
    best_D, best_W, best_T = result[i, j, k, 1:]
    print(f"Max MS = {best_MS:.3f} at D = {best_D:.6f}, W = {best_W:.6f}, T = {best_T:.6f}")

    


