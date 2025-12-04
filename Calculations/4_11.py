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



def run(config,geometry,loads):
    smax=config["Max_Stress"]
    old=config["4_7_Forces"]
    D2=geometry["D2"]
    t2=geometry["t2"]
    Asm=np.pi*D2**2/4
    delta_T_min=-5
    delta_T_max=15
    alpha_fastner=config["a_b"]
    alpha_clamped=config["a_c"]
    Eb=config["Eb"]
    Lj=geometry["Lj"]
    phi=config["phi"]
    
    FdTmin=(alpha_clamped-alpha_fastner)*delta_T_min*Eb*Asm*(1-phi)
    FdTmax=(alpha_clamped-alpha_fastner)*delta_T_max*Eb*Asm*(1-phi)
    
    Fmin=FdTmin+old
    Fmax=FdTmax+old
    
    stress_min=Fmin/D2/t2
    stress_max=Fmax/D2/t2

    
    
    return (stress_min<=smax)&(stress_max<=smax)
