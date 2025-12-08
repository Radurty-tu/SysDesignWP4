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



def run(config,D2,t2,t3,stress1,stress2,smax1,smax2,phi,Eb,Es,alpha_fastner,alpha_clamped):
    D2=D2/1000
    t2=t2/1000
    t3=t3/1000
    Asm=np.pi*D2**2/4
    delta_T_min=-5
    delta_T_max=15
    alpha_spacecraft=config["as"]
    
    
    FdTminc=(alpha_clamped-alpha_fastner)*delta_T_min*Eb*Asm*(1-phi)
    FdTmaxc=(alpha_clamped-alpha_fastner)*delta_T_max*Eb*Asm*(1-phi)
    
    FdTmins=(alpha_spacecraft-alpha_fastner)*delta_T_min*Es*Asm*(1-phi)
    FdTmaxs=(alpha_spacecraft-alpha_fastner)*delta_T_max*Es*Asm*(1-phi)
    
    
    stress_minc=FdTminc/D2/t2+stress1
    stress_maxc=FdTmaxc/D2/t2+stress1
    
    stress_mins=FdTmins/D2/t3+stress2
    stress_maxs=FdTmaxs/D2/t3+stress2

    
    
    return [(stress_minc<=smax1)&(stress_maxc<=smax1),(stress_mins<=smax2)&(stress_maxs<=smax2),stress_maxc-stress1,stress_maxs-stress2]
