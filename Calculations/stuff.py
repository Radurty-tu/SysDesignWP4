def run_it(configA,geometry,loads,loadFilePath,export=True): #change the export to false if you don't want an excel
    import numpy as np
    import pandas as pd
    import math
    from Calculations._4_11 import run

    forceX = np.array([loads["FX"],0.0,0.0])
    forceY = np.array([0.0,loads["FY"],0.0])
    forceZ = np.array([0.0,0.0,loads["FZ"]])
    all_moments = np.array([loads["MX"],loads["MY"],loads["MZ"]])/1e-3 #must be in N mm !!!

    max_t2 = geometry["T2_max"]/1e-3 #in mm and again to be changed/decided
    min_t2 = geometry["T2_min"]/1e-3 #in mm!
    max_length = geometry["max_length"]*1e+3 #in mm max horizontal length TBD
    twall = 0.5 #to be set
    t_extra_max = 40
    #t_extra defined in the d2 loop

    size_factor = 1.5 #just the ratio between the shank and head/nut
    space_material = {"name": "7475-T 761", "elasticity": 70*1e+9, "density": 2810,
                      "max_STRESS": 448*1e+6,"max_SHEAR":310*1e+6,"expansion":23.2*1e-6}

    bolt_material = [ #these are for the bolts, E_b is quite important for compatibility
        {"name": "2014-T6", "elasticity": 73.1 * 1e+9, "density": 2800,
         "max_STRESS": 414 * 1e+6, "max_SHEAR": 290 * 1e+6, "expansion": 23*1e-6 },
        {"name": "7075-T6", "elasticity": 71.7 * 1e+9, "density": 2810,
         "max_STRESS": 503 * 1e+6, "max_SHEAR": 331 * 1e+6, "expansion": 23.6*1e-6 },
        {"name": "AZ91C-T6", "elasticity": 44.8 * 1e+9, "density": 1810,
         "max_STRESS": 145 * 1e+6, "max_SHEAR": 150 * 1e+6,"expansion": 26*1e-6 },
        {"name": "356-T6", "elasticity": 62.4 * 1e+9, "density": 2670,
         "max_STRESS": 165 * 1e+6, "max_SHEAR": 143 * 1e+6,"expansion": 21.4*1e-6 },
        {"name": "4130 Steel", "elasticity": 205 * 1e+9, "density": 7850,
         "max_STRESS": 435 * 1e+6, "max_SHEAR": 430 * 1e+6,"expansion": 11.1*1e-6 },
        {"name": "8630 Steel", "elasticity": 200 * 1e+9, "density": 7850,
         "max_STRESS": 550 * 1e+6, "max_SHEAR": 410 * 1e+6,"expansion": 11*1e-6 },
        {"name": "2024-T3", "elasticity": 73.1 * 1e+9, "density": 2780,
         "max_STRESS": 345 * 1e+6, "max_SHEAR": 283 * 1e+6,"expansion": 23.2*1e-6 },
        {"name": "2024-T4", "elasticity": 73.1 * 1e+9, "density": 2780,
         "max_STRESS": 324 * 1e+6, "max_SHEAR": 283 * 1e+6,"expansion": 23.2*1e-6 },
    ]
    main_material = bolt_material[configA["Material"]] #get the material
    mp_i = 0
    for pos,dictionary in enumerate(bolt_material):
        if main_material["name"] == dictionary["name"]:
            mp_i = pos #removes the material we use for main for we cannot repeat it
            break #exit loop
    bolt_material.pop(mp_i)

    h = geometry["H"] * 1e+3 # in mm the inter-flange distance
    path = loadFilePath
    # load the data from the file
    data = np.load(path)
    results = data["result"]
    ms_values = results[..., 0]
    d1_values = results[..., 1] * 1e+3
    w_values = results[..., 2] * 1e+3
    t_values = results[..., 3] * 1e+3
    valid_mask = ms_values != 0
    valid_wtd = np.column_stack((w_values[valid_mask], t_values[valid_mask], d1_values[valid_mask]))
    unique_wtd = np.unique(valid_wtd, axis=0)  # Unique inputs to solve for

    min_d2,max_d2 = geometry["D2_min"]*1e+3, geometry["D2_max"]*1e+3
    steps = max(1, int(round(abs(max_d2 - min_d2))) + 1)
    diameter_list = list(np.linspace(min_d2, max_d2, num=steps))
    bolt_configs = [ #all 5 options, more can be added if necessary
        {"name": "2_each", "ID": 2, "rows": [2], "d2_list": diameter_list},
        {"name": "3_each", "ID": 3, "rows": [3], "d2_list": diameter_list},
        {"name": "2,2_each","ID": 22, "rows": [2,2], "d2_list": diameter_list},
        {"name": "3,3_each","ID": 33, "rows": [3,3],  "d2_list": diameter_list}
    ]
    ##########
    def bearing_check(n_f,fX,fZ,d_two,thickness,max_stress,max_stress_w,thick_wall,mY,clearance,rows,length,b_w,
                      sMin,extraS=0,extraSw=0): # we are assuming center cg (0,0,0) so no need to calculate that
        f_inX = np.array([fX/n_f,0.0,0.0]) # we are also assuming same d_2 for all
        f_inZ = np.array([0.0,0.0,fZ/n_f]) # we call this for t_2 and t_wall eventually
        extraF = np.array([0.0,0.0,0.0])
        if mY != 0:
            posi = []  # we use 0,0,0 as the cg
            x_crd = -length / 2 + clearance
            for col in range(len(rows)):  # one side only
                z_limits = [-b_w / 2 + clearance, b_w / 2 - clearance]
                z_crds = np.linspace(z_limits[0], z_limits[1], rows[col])
                if rows[col] == 1:
                    z_crds = np.array([0.0])
                for zc in z_crds:
                    posi.append([math.pi * (d_two / 2) ** 2, x_crd, zc, d_two])
                if col < len(rows) - 1:
                    x_crd += sMin
            posi = np.array(posi) #all are in mm or mm² in posi
            mirror = posi.copy()
            mirror[:, 1] = mirror[:, 1] * -1
            posi = np.vstack((posi, mirror))
            # calculate the polar moment for x and z
            polar_x = np.sum(posi[:, 0] * (posi[:, 1] ** 2))
            polar_z = np.sum(posi[:, 0] * (posi[:, 2] ** 2))
            polar_tot = polar_x + polar_z
            r = np.column_stack((posi[:,1],posi[:,1] * 0,posi[:,2]))
            sign = np.sign(mY)
            r_mag = np.sqrt(r[:,0]**2 + r[:,2]**2) #only magnitude
            r_perp_unit = np.cross(r/r_mag[:,None],np.array([0.0,-1*sign,0.0]))
            posi = np.column_stack((posi,r_mag))
            # the reaction forces will cause a negative moment (clockwise)
            mForce_My = (mY / polar_tot) * (posi[:, 0] * r_mag) #array of magnitudes
            extraF = mForce_My[:,None] * r_perp_unit
            #
        forces_all = f_inX + f_inZ + extraF #sign taken into account
        total_f = np.sqrt(forces_all[:,0]**2 + forces_all[:,2]**2)
        stress = (np.max(total_f) / (d_two * thickness)) * 1e+6 + extraS #change to Pa we used mm² before
        stress_wall = (np.max(total_f)/(d_two * thick_wall)) * 1e+6 + extraSw #change to Pa
        ms_bear,ms_bear_w = (max_stress/stress - 1),(max_stress_w/stress_wall - 1)
        passed_plate = True if stress <= max_stress else False
        passed_wall = True if stress_wall <= max_stress_w else False
        return passed_plate,passed_wall,ms_bear,ms_bear_w

    def pullout_check(arm_l,force_X,force_Y,force_Z,rows,clearance,w_height,d__2,min_s,length,max_shear
                      ,max_shear_w,th,th_wall,ext_moments):
        #position the fastners as far from cg as possible
        positions = [] # we use 0,0,0 as the cg
        num = 2 * sum(rows)
        x_crd = -length/2 + clearance
        for col in range(len(rows)):  # one side only
            z_limits = [-w_height/2 + clearance, w_height/2 - clearance]
            z_crds = np.linspace(z_limits[0], z_limits[1], rows[col])
            if rows[col] == 1:
                z_crds = np.array([0.0])
            for zc in z_crds:
                positions.append([math.pi * (d__2 / 2)**2, x_crd, zc, d__2])
            if col < len(rows)-1:
                x_crd += min_s
        positions = np.array(positions)
        mirror = positions.copy()
        mirror[:,1] = mirror[:,1] * -1
        positions = np.vstack((positions,mirror))
        # calculate the polar moment for x and z
        polar_x = np.sum(positions[:,0] * (positions[:,1]**2))
        polar_z = np.sum(positions[:,0] * (positions[:,2]**2))
        vector_p = np.array([0.0,arm_l,0.0])
        moments = np.cross(vector_p,(force_X + force_Y + force_Z)) + ext_moments #moments due to X and Z
        tension_force = force_Y[1]/num #force per fastner, positive is tension
        #forces due to the moments x and z
        mForce_Mx = (moments[0] / polar_z) * (positions[:, 0] * positions[:, 2])
        mForce_Mz = -1 * (moments[2] / polar_x) * (positions[:, 0] * positions[:, 1])
        total_T_forces = mForce_Mx + mForce_Mz + tension_force
        side_area = (math.pi * positions[:, 3] * th) / 1e+6 # in Pa
        side_area_wall = (math.pi * positions[:, 3] * th_wall) / 1e+6
        shear_stresses = np.round(total_T_forces / side_area)
        shear_wall = np.round(total_T_forces / side_area_wall)
        app_shear_max = np.max(np.abs(shear_stresses))
        app_shear_max_w = np.max(np.abs(shear_wall))
        ms_pull,ms_pull_w = (max_shear/app_shear_max - 1),(max_shear_w/app_shear_max_w - 1)
        cool = True if app_shear_max <= max_shear else False
        cool_2 = True if app_shear_max_w <= max_shear_w else False
        return cool,cool_2,ms_pull,ms_pull_w

    def compliance_check(b_mat,t_wall,t_backplate,diameter,main_mat,sc_mat,s_factor,hexa,tight,max_f):
        diam_m = diameter/1e+3 #to get it to m
        d_outer = diam_m * s_factor
        delta_backplate = (4*t_backplate/1e+3)/(main_mat["elasticity"] * np.pi * (d_outer**2 - diam_m**2))
        delta_wall = (4*t_wall/1e+3)/(sc_mat["elasticity"] * np.pi * (d_outer**2 - diam_m**2))
        delta_att = delta_wall + delta_backplate

        a_nom = (np.pi * (diam_m/2)**2)  # the area with inner diameter in m²
        h_factor = 0.5 if hexa else 0.4  # hex and cyl
        eng_factor = 0.4 if tight else 0.33 #will likely be true always as we want higher coefficients
        n_factor = 0.4  # always
        l_head_sub = diam_m * h_factor
        l_eng_sub = diam_m * eng_factor
        l_shank_sub = (t_backplate + t_wall) / 1e+3
        l_nut_sub = diam_m * n_factor
        delta_b = (l_head_sub + l_eng_sub + l_shank_sub + l_nut_sub) / (a_nom * b_mat["elasticity"])

        comp = delta_att/(delta_att + delta_b)
        good = True if comp < max_f else False
        return good, comp

    def mass_calc(bolt_m,main_m,sc_m,thick_plate,l,b_diam,nrows,t1,w_flange,d_one,extra):
        n_fast = sum(nrows)
        w_flange_m = w_flange/1e+3
        t1_m = t1/1e+3
        t2_m = thick_plate/1e+3
        l_m = l/1e+3
        b_diam_m = b_diam/1e+3
        d_one_m = d_one/1e+3
        density_hinge = main_m["density"] #in SI units
        density_b = bolt_m["density"] #in SI units
        volume_backplate = (t2_m * l_m) - (np.pi * (b_diam_m/2)**2) * n_fast #plate - holes
        angle_ratio = (2 * np.arccos((d_one_m/2)/(d_one_m/2 + w_flange_m-d_one_m)))/(np.pi*2)
        flange_volume = (2 * t1_m) * w_flange_m + (np.pi * (w_flange_m**2 - d_one_m**2) * t1_m) * (1-angle_ratio)
        est_head_nut_extra_l = 3 * b_diam_m
        bolt_volume = n_fast * ((t1_m + t2_m + est_head_nut_extra_l)*np.pi*(b_diam_m/2)**2)
        #extra
        mass_extra = (extra/1e+3 * l_m * w_flange_m) * sc_m
        #
        hinge_mass = (flange_volume + volume_backplate) * density_hinge
        bolt_mass = bolt_volume * density_b
        total_mass = hinge_mass + bolt_mass + mass_extra
        return total_mass

    ##########
    all_info = []
    for index in range(len(bolt_material)): #iterate over every bolt material available
        max_STRESS = bolt_material[index]["max_STRESS"]
        max_SHEAR = bolt_material[index]["max_SHEAR"]
        max_STRESS_w = main_material["max_STRESS"]
        max_SHEAR_w = main_material["max_SHEAR"]
        last_info = []
        for p in range(len(unique_wtd)): #feeds the system a given combination of w,t1,d1
            w_input = unique_wtd[p, 0]
            t1_input = unique_wtd[p, 1]
            d1_input = unique_wtd[p, 2]
            s = 1 * d1_input  # the distance from face of backplate to the edge of d_1, k=1 as a conservative value
            config_best_comb = [] #having filtered all d_2 we now choose the best config for all configs
            for config in bolt_configs: # for one loop we have a given topological configuration
                rows_cfg = config["rows"]
                rows_id = config["ID"]
                d_2_best_comb = [] #fixed for a given w,t1,d1 and config, this also resets after each d_2 full loop
                for d_2 in config["d2_list"]: #for each top. config we try all d_2s
                    t_extra = 0
                    max_in_column = max(rows_cfg)
                    number = 2 * sum(rows_cfg) #number of fasteners total
                    s_min = 2 * d_2
                    clear = 1.5 * d_2
                    # we check that the bolt sizes actually fit in the height w, if they don't onto the next d_2
                    if (clear * 2) + s_min * (max_in_column-1) > w_input:
                        break #if it does not fit we exit the loop completely so higher d_2 are not tested

                    # Check if max thickness and length is enough to pass, if not skip d_2
                    max_wall_t_check = twall + t_extra_max
                    pass_bear_max, pass_wall_max, _, _ = bearing_check(number, forceX[0], forceZ[2], d_2, max_t2,
                                                                       max_STRESS, max_STRESS_w, max_wall_t_check,
                                                                       all_moments[1], clear, rows_cfg, max_length,
                                                                       w_input, s_min)
                    if not (pass_bear_max and pass_wall_max):
                        continue  # Bearing failed even at max dims, skip d_2

                    l_arm_max = max_t2 + d1_input / 2 + s
                    pass_pull_max, pass_p_wall_max, _, _ = pullout_check(l_arm_max, forceX, forceY, forceZ, rows_cfg,
                                                                         clear, w_input, d_2, s_min, max_length,
                                                                         max_SHEAR, max_SHEAR_w, max_t2,
                                                                         max_wall_t_check, all_moments)
                    if not (pass_pull_max and pass_p_wall_max):
                        continue # Pullout failed even at max dims, skip d_2
                    # ----------------- OPTIMIZATION END -----------------

                    wall_t = twall + t_extra
                    # we assume symmetric about cg so no moments, we can check bearing without getting r positions
                    curr_t2 = min_t2
                    curr_length = (2 * t1_input + h) + 2 * clear + (len(rows_cfg) - 1) * s_min
                    abs_minLength = curr_length
                    def get_best_bearing(b_curr_t2,b_twall,b_t_extra,b_t_extra_max,b_curr_length,
                                        b_number, b_forceX, b_forceZ, b_d_2,
                                        b_max_STRESS, b_max_STRESS_w, b_Y_moments,b_clear,b_rows_cfg,
                                        b_w_input,b_s_min,b_minLength,extS,extSw,fix_t=False):
                        failed_b = False
                        b_wall_t = b_twall + b_t_extra
                        pass_bearing,pass_b_wall,sF_bear,sF_bear_w = bearing_check(b_number, b_forceX, b_forceZ, b_d_2, b_curr_t2,
                                                                 b_max_STRESS,b_max_STRESS_w,b_wall_t,b_Y_moments,
                                                                 b_clear,b_rows_cfg,b_curr_length,b_w_input,b_s_min,extS,extSw)

                        while not all((pass_bearing,pass_b_wall)): #call the function get true if passed false if not
                            if b_curr_length < max_length:  # if it fails we first ALWAYS check if we can increase length
                                b_curr_length += 1
                            else:  # if we cannot, we distinguish between backplate and wall
                                if fix_t: #special variable from pullout, we don't iterate t2 just length
                                    failed_b = True
                                    break

                                if not pass_bearing:  # if the plate fails increase t2
                                    if b_curr_t2 < max_t2:
                                        b_curr_t2 += 1  # increase t_2 and try again
                                        b_curr_length = b_minLength
                                    else:
                                        failed_b = True
                                        break
                                else:  # the wall failed and we at max Length
                                    if b_t_extra < b_t_extra_max:
                                        b_t_extra += 1
                                        b_wall_t = b_twall + b_t_extra  # we reset the length after increased thickness
                                        b_curr_length = b_minLength
                                    else:
                                        failed_b = True
                                        break  # try for higher d2
                            #outside main if
                            if not failed_b: #only run if we actually have valid inputs
                                pass_bearing, pass_b_wall,sF_bear,sF_bear_w = bearing_check(b_number, b_forceX, b_forceZ, b_d_2, b_curr_t2,
                                                                 b_max_STRESS,b_max_STRESS_w,b_wall_t,b_Y_moments,
                                                                 b_clear,b_rows_cfg,b_curr_length,b_w_input,b_s_min,extS,extSw)
                        return b_curr_t2,b_t_extra,b_curr_length,failed_b,sF_bear,sF_bear_w
                    #outside function
                    curr_t2,t_extra,curr_length,failed_bearing,sf_bear,sf_bear_w = get_best_bearing(curr_t2,twall,t_extra,
                                                         t_extra_max,curr_length,
                                                         number,forceX[0], forceZ[2], d_2, max_STRESS,
                                                         max_STRESS_w,all_moments[1],clear,rows_cfg,
                                                         w_input,s_min,abs_minLength,0.0,0.0)

                    if failed_bearing: continue
                    # we must now try the pullout check with our latest t_2
                    current_min_length = curr_length #from bearing check
                    l_arm = curr_t2 + d1_input/2 + s #the length from force to shear plane
                    failed_pullout = False
                    pass_pullout, pass_p_wall,sf_pull,sf_pull_w = pullout_check(l_arm,forceX,forceY,forceZ,rows_cfg,clear,
                                            w_input,d_2,s_min,curr_length,max_SHEAR,max_SHEAR_w,
                                                              curr_t2,wall_t,all_moments) #this must get the positions and new length so basically all
                    while not all((pass_pullout,pass_p_wall)):
                        if curr_length < max_length: #if it fails we first ALWAYS check if we can increase length
                            curr_length += 1
                        else: #if we cannot we distinguish between backplate and wall
                            if not pass_pullout: #if the plate fails increase t2
                                if curr_t2 < max_t2:
                                    curr_t2 += 1  # increase t_2 and try again
                                    l_arm = curr_t2 + d1_input / 2 + s  # the length from force to shear plane
                                    curr_length = abs_minLength
                                    _,_,curr_length,*_,sf_bear,sf_bear_w = get_best_bearing(curr_t2,twall,t_extra,t_extra_max,curr_length,
                                                         number,forceX[0], forceZ[2], d_2, max_STRESS,max_STRESS_w,
                                                        all_moments[1],clear,rows_cfg,w_input,s_min,abs_minLength,0.0,0.0,True)
                                    # reset length with new t_2, min length for new bearing done by function
                                else:
                                    failed_pullout = True
                                    break
                            else: #the wall failed and we at max Length
                                if t_extra < t_extra_max:
                                    t_extra += 1
                                    wall_t = twall + t_extra #we rest the length after increase in thickness
                                    curr_length = abs_minLength
                                    _,_,curr_length,*_,sf_bear,sf_bear_w = get_best_bearing(curr_t2, twall, t_extra, t_extra_max,curr_length,
                                                          number, forceX[0], forceZ[2], d_2, max_STRESS,max_STRESS_w,
                                                          all_moments[1], clear, rows_cfg,w_input,s_min,abs_minLength,0.0,0.0,True)
                                    # reset length with new t_wall, min length for new bearing
                                else:
                                    failed_pullout = True
                                    break #try for higher d2
                        #outside main if
                        if not failed_pullout:  # only run if we actually have valid inputs
                            pass_pullout, pass_p_wall,sf_pull,sf_pull_w = pullout_check(l_arm, forceX, forceY, forceZ, rows_cfg, clear,
                                                                  w_input, d_2, s_min, curr_length, max_SHEAR, max_SHEAR_w,
                                                                  curr_t2,wall_t,all_moments)  # this must get the positions and new length so basically all
                    if failed_pullout: continue
                    # we now check the compliance, the max value is 0.3 which can be changed
                    max_force_ratio = 0.3
                    hexagonal = True  # hex and cyl
                    n_tightened = True
                    pass_compliance,comp = compliance_check(bolt_material[index],wall_t,curr_t2,d_2,main_material,space_material,
                                            size_factor,hexagonal,n_tightened,max_force_ratio)
                    if not pass_compliance:
                        continue #the only way to decrease compliance is by increasing d_2 so we do that

                    m_s_bearing, m_s_bearing_w = (sf_bear+1)*max_STRESS,(sf_bear_w+1)*max_STRESS_w
                    pass_thermal,pass_thermal_w,ext_S,ext_S_w = run(configA,d_2,curr_t2,wall_t,m_s_bearing,m_s_bearing_w,max_STRESS,max_STRESS_w,comp,
                    main_material["elasticity"],space_material["elasticity"],bolt_material[index]["expansion"],main_material["expansion"])
                    #if it fails we have to increase t2 and/or t_wall and rerun the loop again with a new thickness
                    failed_total = False
                    while not all((pass_thermal,pass_thermal_w)):
                        if curr_length < max_length:
                            curr_length += 1 #we try decreasing the bearing stress before addressing thermal
                            curr_t2, t_extra, curr_length, failed_bearing, sf_bear, sf_bear_w = get_best_bearing(
                                curr_t2, twall, t_extra, t_extra_max, curr_length,
                                number, forceX[0], forceZ[2], d_2, max_STRESS, max_STRESS_w, all_moments[1],
                                clear, rows_cfg, w_input, s_min, abs_minLength, ext_S, ext_S_w)
                            pass_pullout, pass_p_wall, sf_pull, sf_pull_w = pullout_check(l_arm, forceX, forceY,
                                                            forceZ, rows_cfg, clear,w_input, d_2,s_min, curr_length,
                                                            max_SHEAR,max_SHEAR_w, curr_t2, wall_t,all_moments)
                                                        # this must get the positions and new length so basically all
                        else:
                            if not pass_thermal:
                                if curr_t2 < max_t2:
                                    curr_t2 += 1
                                    #curr_length = abs_minLength
                                    curr_t2, t_extra, curr_length, failed_bearing, sf_bear, sf_bear_w = get_best_bearing(
                                        curr_t2, twall, t_extra,t_extra_max, curr_length,
                                        number, forceX[0], forceZ[2], d_2, max_STRESS,max_STRESS_w, all_moments[1],
                                        clear, rows_cfg, w_input, s_min, abs_minLength,ext_S,ext_S_w)
                                    pass_pullout, pass_p_wall, sf_pull, sf_pull_w = pullout_check(l_arm, forceX, forceY,
                                                                                    forceZ, rows_cfg,clear,w_input, d_2,
                                                                                    s_min,curr_length,max_SHEAR,
                                                                max_SHEAR_w,curr_t2, wall_t,all_moments)  # this must get the positions and new length so basically all
                                else: #try next d2 see if the bearing stresses are lower
                                    failed_total = True
                                    break
                            if not pass_thermal_w:
                                if t_extra < t_extra_max:
                                    t_extra += 1
                                    #curr_length = abs_minLength
                                    wall_t = twall + t_extra
                                    curr_t2, t_extra, curr_length, failed_bearing, sf_bear, sf_bear_w = get_best_bearing(
                                        curr_t2, twall, t_extra, t_extra_max, curr_length, number, forceX[0],
                                        forceZ[2], d_2, max_STRESS,max_STRESS_w, all_moments[1], clear, rows_cfg,
                                        w_input, s_min, abs_minLength,ext_S,ext_S_w)
                                else: #try next d2
                                    failed_total = True
                                    break
                        pass_thermal, pass_thermal_w, ext_S, ext_S_w = run(configA, d_2, curr_t2, wall_t, m_s_bearing,
                                                                           m_s_bearing_w, max_STRESS, max_STRESS_w,comp,
                                                                           main_material["elasticity"],space_material["elasticity"],
                                                                           bolt_material[index]["expansion"],main_material["expansion"])
                    if failed_total: continue
                    #if the design has made it this far it has passed, now we need a mass calc to rank all decent results
                    mass_i = mass_calc(bolt_material[index],main_material,space_material["density"],curr_t2,
                                       curr_length,d_2,rows_cfg,t1_input,
                                     w_input,d1_input,t_extra)
                    info = [curr_t2,curr_length,d_2,mass_i,sf_bear,sf_bear_w,sf_pull,sf_pull_w,comp]
                    d_2_best_comb.append(info)

                #we are outside the d_2 loop so the d_2 list has all d_2 values for a given config and fixed vals
                if d_2_best_comb:
                    d_2_best_comb = np.array(d_2_best_comb)
                    index_mass = np.argmin(d_2_best_comb[:,3]) #min mass
                    new_info = np.append(d_2_best_comb[index_mass],rows_id)
                    config_best_comb.append(new_info)

            #we are outside the config loop so we have checked all configs, now decide which is best for the fixed vals
            if config_best_comb:
                config_best_comb = np.array(config_best_comb)
                index_mass2 = np.argmin(config_best_comb[:,3])  # min mass
                last_info.append(np.append(config_best_comb[index_mass2],np.array([w_input,d1_input,t1_input])))
                #contains best d_2,l,t2,config for a fixed value of t1,w1,d1 so one iteration

        #we are outside the fixed value loop so the t1,w1,d1 loop but still inside bold material loop
        #so last info is essentially a list of best combination for each t1,w1,d1 combination [[comb1],[comb2],[],[],...]
        all_info.append(last_info) #contains last_info for all materials so [mat1[[comb1],[comb2]],mat2[[],[]],...[...]]
        #export to excell
    if export:
        header_names = ["Plate Thickness 2 (mm)","Plate Length (mm)","Fastener Diameter (mm)",
                        "Mass (kg)","MS Bearing Plate","MS Bearing Wall","MS Pullout Plate","MS Pullout Wall","Compliance",
                        "Fastener Configuration","Plate Height w (mm)","Diameter Lug Hole (mm)",
                        "Flange Thickness (mm)"]
        sheet_names = [dic["name"] for dic in bolt_material] #array of material names one for each sheet
        fileName = f'Hinge_{main_material["name"]}_combinations.xlsx'
        numpy_export = []
        with pd.ExcelWriter(fileName) as writer: #open the excel file and write on it
            for a, combinations in enumerate(all_info): #loop over materials and combinations is the big ass list inside
                dataFrame = pd.DataFrame(combinations,columns = header_names)
                name_sheet = sheet_names[a] #each sheet will have the name of the material for the fastener
                dataFrame.to_excel(writer,sheet_name = name_sheet,index = False)
                #np
                combinationss = np.array([combinations])
                np.savez(f'{a}_numpy_file',
                         t2 = combinationss[:,0],
                         length = combinationss[:,1],
                         d2 = combinationss[:,2],
                         mass = combinationss[:,3],
                         ms_bearing = combinationss[:,4],
                         ms_bearing_wall = combinationss[:,5],
                         ms_pullout = combinationss[:,6],
                         ms_pullout_wall = combinationss[:,7],
                         config = combinationss[:,8],
                         height = combinationss[:,9],
                         d1 = combinationss[:,10],
                         t1 = combinationss[:,11]
                         )

    print("Done")
    return all_info #path to file
