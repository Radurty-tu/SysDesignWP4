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

def fastner_check(loads,fastners):
    FY = loads["FY"]
    MZ = loads["MZ"]
    flist=fastners["Coords"]
    Alist=fastners["Area"]
    
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
    
    
    
    return





