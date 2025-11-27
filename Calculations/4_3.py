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
import json
def design_lug(geometry,loads,config):
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
    N     = geometry["N"]
    
    FX = loads["FX"]
    FY = loads["FY"]
    FZ = loads["FZ"]
    F1 = loads["F1"]
    MX = loads["MX"]
    
    FTY  = config["FTY" ]
    FTU  = config["FTU" ]
    FBR  = config["FBR" ]
    KT   = config["KT"  ]
    KBRY = config["KBRY"]
    SF   = config["SF"  ]
    FMIS = config["FMIS"]
    
    
    #Numpy
    D_vals = np.linspace(D_min, D_max, N)
    W_vals = np.linspace(W_min, W_max, N)
    T_vals = np.linspace(T_min, T_max, N)
    D_grid, W_grid, T_grid = np.meshgrid(D_vals, W_vals, T_vals, indexing='ij')
    cube = (D_grid + W_grid + T_grid < 1.0).astype(float)
    
    
    #edge distance
    #E=(W-D1)/2
    #Net-Tension Area
    #AT=T1*(W-D1)
    #SHEAR AREA AXIAL
    #ABRA=T1*D1
    #SHEAR AREA SHEAR
    #ABRS=T1*E
    
    #--- FAILURE MODES ---
    
    # NET-TENSION FAILURE
    #MAX LOAD = STRESS CONCENTRATION * MAX MATERIAL IDK * AT
    #PU=KT*FTU*AT
    
    #SHEAR OUT BEARING
    #MAX LOAD = STRESS CONCENTRATION * MAX MATERIAL IDK * ABR
    #PBRY=KBRY*FTU*ABR
    
    #BUSHING YIELD
    #PBRY= 1.85*FCY*ABR
    
    
    
    return