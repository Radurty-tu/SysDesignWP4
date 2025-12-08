'''
Black box diagram
yeah



output:
    phi
'''
import numpy as np
from Data import material_properties as mp

def run(config,geometry,loads):
    D2_min = float(geometry["D2_min"])
    D2_max = float(geometry["D2_max"])
    t2_min = float(geometry["t2_min"])
    t2_max = float(geometry["t2_max"])
    t3_min=geometry["t3_min"]
    t3_max=geometry["t3_max"]
    N=geometry["N"]
    size_factor=geometry["size_factor"] #Dfo=D2*this
    mat=config["Material"]
    E_lug=mp.get_material(mat,"elasticity")
    E_bolt=mp.get_material(mat,"elasticity")
    E_wall=mp.get_material(0,"elasticity")
    h_factor=0.5
    eng_factor=0.4
    n_factor=0.4
    D2_arr = np.linspace(D2_min, D2_max, N)
    t2_arr = np.linspace(t2_min, t2_max, N) 
    t3_arr = np.linspace(t3_min, t3_max, N)
    D2_grid, t2_grid, t3_grid = np.meshgrid(D2_arr, t2_arr, t3_arr, indexing="ij")
    Dfo_grid = size_factor * D2_grid
    ring_area = np.pi * (Dfo_grid**2 - D2_grid**2)
    delta_lug = 4.0 * t2_grid / (E_lug*ring_area)
    delta_wall = 4.0 * t3_grid / (E_wall * ring_area)
    delta_att = delta_lug + delta_wall
    
    A_nom = np.pi * (D2_grid / 2.0)**2
    l_head  = h_factor  * D2_grid
    l_eng   = eng_factor* D2_grid
    l_shank = t2_grid + t3_grid
    l_nut   = n_factor   * D2_grid
    L_bolt = l_head + l_eng + l_shank + l_nut
    delta_b = L_bolt / (E_bolt * A_nom)
    phi = delta_att / (delta_att + delta_b)
    output_path = "./Data/phi_4_10.npz"
    np.savez(
        output_path,
        D2_arr=D2_arr,
        t2_arr=t2_arr,
        t3_arr=t3_arr,
        phi=phi
    )
    return output_path


