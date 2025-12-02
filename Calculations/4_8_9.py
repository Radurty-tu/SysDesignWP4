'''
Black box diagram
inputs:
    nf -fastner count
        (xi,zi) coords
        Ai- area (4.4-4.7)
    Fy 4.1
    Mz 4.1
    
    

outputs:
    Fpi
    FpMz
    
    
    
'''

#Fpi=Fy/nf
#FpMz=Mz*Ai*ri/sigma (Airi**2)

import numpy as np
import matplotlib.pyplot as plt
def fastner_check(loads,fastners,config):
    FY = loads["FY"]
    MZ = loads["MZ"]
    flist=fastners["Coords"]
    Alist=fastners["Area"]
    DF=fastners["Diameter"]
    T2=config["T2"] #Thickness of the lug backup wall.
    T3=config["T3"] #Thickness of the vehicle wall.
    Y2=config["Y2"] #Tensile yield strength of the lug backup wall material.
    Y3=config["Y3"] #Tensile yield strength of the vehicle wall material.
    
    weighted = flist * Alist[:, None]
    xcg = weighted[:,0].sum()/Alist.sum()
    zcg = weighted[:,1].sum()/Alist.sum()
    
    ri = np.sqrt((flist[:,0] - xcg)**2 + (flist[:,1] - zcg)**2)
    nf=len(flist)
    Fpi=FY/nf
    sigma=np.sum(Alist * ri**2)
    FpMz=MZ*Alist*ri/sigma
    sign_z = np.sign(flist[:, 1] - zcg)
    FpMz=FpMz*sign_z
    
    FYi= Fpi+FpMz
    #end of 4.8
    TAUy2=Y2/np.sqrt(3)
    TAUy3=Y3/np.sqrt(3)
    
    A2=np.pi*DF*T2
    A3=np.pi*DF*T3
    
    TAU2=FYi/A2
    TAU3=FYi/A3
    
    MS2=np.abs(TAUy2/TAU2) - 1
    MS3=np.abs(TAUy3/TAU3) - 1
    
    
    
    return MS2,MS3



if __name__ == "__main__":
    # Random but realistic configuration
    loads = {
        "FY": 12_000.0,     # N    (axial out-of-plane load)
        "MZ": 1_500.0       # N·m  (bending moment about z)
    }

    # Example 6-fastener pattern
    nf = 6
    # coords in meters
    coords = np.array([
        [-0.015, -0.012],
        [-0.015,  0.012],
        [ 0.000, -0.012],
        [ 0.000,  0.012],
        [ 0.015, -0.012],
        [ 0.015,  0.012],
    ])

    # Areas from 4.4–4.7 (example: head/nut bearing annular area)
    areas = np.full(nf, 45e-6)   # m²  (≈ 45 mm²)

    # Fastener “inner diameter” under head (Dfi) in meters
    df = np.full(nf, 0.006)      # 6 mm

    fastners = {
        "Coords": coords,
        "Area": areas,
        "Diameter": df
    }

    # Wall/material data
    config = {
        "T2": 0.0035,     # m  (3.5 mm backup wall)
        "T3": 0.0040,     # m  (4 mm vehicle wall)
        "Y2": 310e6,      # Pa (aluminum alloy yield)
        "Y3": 350e6       # Pa (stronger wall material)
    }

    # Call your function
    MS2, MS3 = fastner_check(loads, fastners, config)

    # Plot margins per fastener
    idx = np.arange(len(MS2))
    width = 0.35

    plt.figure()
    plt.bar(idx - width/2, MS2, width, label="Backup wall (MS2)")
    plt.bar(idx + width/2, MS3, width, label="Vehicle wall (MS3)")

    plt.axhline(0.0, linestyle="--", linewidth=1)
    plt.xlabel("Fastener index")
    plt.ylabel("Margin of safety")
    plt.title("Pull-through margins per fastener")
    plt.legend()
    plt.tight_layout()
    plt.show()

    #::contentReference[oaicite:0]{index=0}

    print("Done.")


