'''
Black box diagram
kinda got tired of doing these

T_min T_max -constants 10-30 celsius
T_ref 15 celsius

alpha_fastner
alpha_clamped

young_fastner

Joint length
delta_T

Stiffness area of the fastner = pi*D2^2/4
phi (????)
-----
FdT=(alpha_clamped-alpha_fastner)*delta_T*Asm*(1-phi)
'''

import numpy as np



def temp_check(config,geometry):
    D2=geometry["D2"]
    Asm=np.pi*D2**2/4
    delta_T_min=-5
    delta_T_max=15
    alpha_fastner=config["a_b"]
    alpha_clamped=config["a_c"]
    Eb=config["Eb"]
    Lj=geometry["Lj"]
    phi=config["phi"]
    
    FdTmin=(alpha_clamped-alpha_fastner)*delta_T_min*Asm*(1-phi)
    FdTmax=(alpha_clamped-alpha_fastner)*delta_T_max*Asm*(1-phi)
    
    
    return