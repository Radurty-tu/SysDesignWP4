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


def design_lug(geometry, loads, config):
    '''
    Evaluate lug safety factors over a grid of diameters, widths, and thicknesses.

    Returns a dictionary containing the 1-D parameter arrays and a 3-D cube of
    available safety factors for each grid point (0 where invalid or below the
    required safety factor).
    '''
    D_min = geometry["D_min"]
    D_max = geometry["D_max"]
    W_min = geometry["W_min"]
    W_max = geometry["W_max"]
    T_min = geometry["T_min"]
    T_max = geometry["T_max"]
    N = geometry["N"]

    FX = loads["FX"]
    FY = loads["FY"]
    FZ = loads["FZ"]
    F1 = loads["F1"]
    MX = loads["MX"]

    FTY = config["FTY"]
    FTU = config["FTU"]
    FBR = config["FBR"]
    KT = config["KT"]
    KBRY = config["KBRY"]
    SF_req = config["SF"]
    FMIS = config["FMIS"]

    # Derived loads
    P = np.sqrt((F1 + FY) ** 2 + FZ ** 2)
    P_lug = P / 2.0
    mis_threshold = FMIS * P
    F_perp = np.abs(FX) if np.abs(FX) >= mis_threshold else mis_threshold

    # Geometry grids
    D_vals = np.linspace(D_min, D_max, N)
    W_vals = np.linspace(W_min, W_max, N)
    T_vals = np.linspace(T_min, T_max, N)
    D_grid, W_grid, T_grid = np.meshgrid(D_vals, W_vals, T_vals, indexing="ij")

    # Derived geometry
    E = (W_grid - D_grid) / 2.0
    AT = T_grid * (W_grid - D_grid)
    ABR_axial = T_grid * D_grid
    ABR_shear = T_grid * E

    valid_geom = (
        (W_grid > D_grid)
        & (E > 0)
        & (D_grid > 0)
        & (W_grid > 0)
        & (T_grid > 0)
    )

    # Allowables
    P_net = KT * FTY * AT
    P_sb = KBRY * FTY * ABR_shear
    P_bear = FBR * ABR_axial

    # Safety factors per mode
    SF_net = np.divide(P_net, P_lug, out=np.full_like(P_net, np.inf), where=P_lug != 0)
    SF_sb = np.divide(P_sb, P_lug, out=np.full_like(P_sb, np.inf), where=P_lug != 0)
    SF_bear = np.divide(P_bear, P_lug, out=np.full_like(P_bear, np.inf), where=P_lug != 0)
    SF_bend = np.divide(
        FTY * T_grid,
        3.0 * F_perp,
        out=np.full_like(T_grid, np.inf),
        where=F_perp != 0,
    )

    SF_comb = np.minimum.reduce([SF_net, SF_sb, SF_bear, SF_bend])
    SF_comb[~valid_geom] = 0.0
    SF_cube = np.where(SF_comb >= SF_req, SF_comb, 0.0)

    return {
        "D_vals": D_vals,
        "W_vals": W_vals,
        "T_vals": T_vals,
        "SF_cube": SF_cube,
    }
