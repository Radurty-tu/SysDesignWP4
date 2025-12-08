'''
Black box diagram
kinda got tired of doing these

T_min T_max -constants 10-30 celsius
T_ref 15 celsius

alpha_fastner
alpha_clamped

young_plate

delta_T

Stiffness area of the fastner = pi*D2^2/4
phi (????)
-----
FdT=(alpha_clamped-alpha_fastner)*delta_T*Asm*(1-phi)
'''

import numpy as np
from Data import material_properties as mp


def run(config,geometry,loads):
    D2_min = float(geometry["D2_min"])
    D2_max = float(geometry["D2_max"])
    t2_min = float(geometry["t2_min"])
    t2_max = float(geometry["t2_max"])
    t3_min = float(geometry["t3_min"])
    t3_max = float(geometry["t3_max"])
    N = int(geometry["N"])
    D2_arr = np.linspace(D2_min, D2_max, N)
    t2_arr = np.linspace(t2_min, t2_max, N)
    t3_arr = np.linspace(t3_min, t3_max, N)
    D2_grid, t2_grid, t3_grid = np.meshgrid(D2_arr, t2_arr, t3_arr, indexing="ij")
    delta_T_min=-5
    delta_T_max=15
    mat=config["Material"]
    alpha_spacecraft=mp.get_material(0,"expansion")
    alpha_clamped=mp.get_material(mat,"expansion")
    alpha_fastner=mp.get_material(mat,"expansion")
    Eb=mp.get_material(mat,"elasticity")
    Es=mp.get_material(0,"elasticity")
    sigma_allow_clamped  = mp.get_material(mat,  "max_STRESS")
    sigma_allow_spacecraft = mp.get_material(0, "max_STRESS")
    
    phi_data = np.load("./Data/phi_4_10.npz")
    phi_grid = phi_data["phi"]
    mech_data = np.load("./Data/fastener_bearing_scan.npz")
    MS7_mech = mech_data["MS7"]
    sigma_mech_clamped_2d = sigma_allow_clamped / (MS7_mech + 1.0)
    sigma_mech_clamped = sigma_mech_clamped_2d[:, :, None] * np.ones((1, 1, N))
    
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma_mech_spacecraft = sigma_mech_clamped * (t2_grid / t3_grid)
        
    Asm = np.pi * (D2_grid**2) / 4.0
    delta_alpha_clamped  = alpha_clamped  - alpha_fastner
    delta_alpha_spacecraft = alpha_spacecraft - alpha_fastner
    with np.errstate(invalid="ignore"):
        FdT_clamped_min  = delta_alpha_clamped  * delta_T_min * Eb * Asm * (1.0 - phi_grid)
        FdT_clamped_max  = delta_alpha_clamped  * delta_T_max * Eb * Asm * (1.0 - phi_grid)
        FdT_spacecraft_min = delta_alpha_spacecraft * delta_T_min * Eb * Asm * (1.0 - phi_grid)
        FdT_spacecraft_max = delta_alpha_spacecraft * delta_T_max * Eb * Asm * (1.0 - phi_grid)

    
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma_th_clamped_min = FdT_clamped_min / (D2_grid * t2_grid)
        sigma_th_clamped_max = FdT_clamped_max / (D2_grid * t2_grid)

        # spacecraft: thickness t3
        sigma_th_spacecraft_min = FdT_spacecraft_min / (D2_grid * t3_grid)
        sigma_th_spacecraft_max = FdT_spacecraft_max / (D2_grid * t3_grid)
        sigma_tot_clamped_min  = sigma_mech_clamped  + sigma_th_clamped_min
    sigma_tot_clamped_max  = sigma_mech_clamped  + sigma_th_clamped_max
    sigma_tot_spacecraft_min = sigma_mech_spacecraft + sigma_th_spacecraft_min
    sigma_tot_spacecraft_max = sigma_mech_spacecraft + sigma_th_spacecraft_max
    
    # We care about the worst (highest) stress magnitude
    sigma_tot_clamped  = np.maximum(np.abs(sigma_tot_clamped_min),
                                np.abs(sigma_tot_clamped_max))
    sigma_tot_spacecraft = np.maximum(np.abs(sigma_tot_spacecraft_min),
                                np.abs(sigma_tot_spacecraft_max))
    with np.errstate(divide="ignore", invalid="ignore"):
        MS_clamped  = sigma_allow_clamped  / sigma_tot_clamped  - 1.0
        MS_spacecraft = sigma_allow_spacecraft / sigma_tot_spacecraft - 1.0
    
    output_path = "./Data/fastener_thermal_bearing_scan_4_11.npz"
    np.savez(
    output_path,
    D2_arr=D2_arr,
    t2_arr=t2_arr,
    t3_arr=t3_arr,
    MS_clamped=MS_clamped,
    MS_spacecraft=MS_spacecraft,)
    
    return output_path


def plot(file, ax):
    #legacy
    return

