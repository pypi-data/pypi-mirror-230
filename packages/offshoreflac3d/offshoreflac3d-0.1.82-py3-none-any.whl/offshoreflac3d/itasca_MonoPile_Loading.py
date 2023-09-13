import numpy as np 
import pandas as pd
import itasca as it
import os
it.command("python-reset-state false")


#0 for Fx, 1 for Fy, 2 for Fz, 3 for Mx, 4 for My, 5 for Mz

def loading(group,load,Type):
    Jx = Jy = Jp = 0
    Node_ref = []
    N = 0
    for sn in it.structure.node.list():
        if sn.group('reference') == group:
            Jx = Jx + sn.pos()[0]**2
            Jy = Jx
            Jp = Jx + Jy
            Node_ref.append(sn)
            N = N + 1

    load_n = load / N

    for sn_ref in Node_ref:
        if Type == 0:
            sn_ref.set_apply(Type,load_n)
        elif Type == 1:
            sn_ref.set_apply(Type,load_n)
        elif Type == 2:
            sn_ref.set_apply(Type,load_n)
        elif Type == 3:
            load_n = load*sn_ref.pos()[1]/Jx
            load_n_final = sn_ref.apply()[0][2] + load_n
            sn_ref.set_apply(Type-1,load_n_final)
        elif Type == 4:
            load_n = -load*sn_ref.pos()[0]/Jy
            load_n_final = sn_ref.apply()[0][2] + load_n
            sn_ref.set_apply(Type-2,load_n_final)
        elif Type == 5:
            r = np.sqrt(sn_ref.pos()[0]**2+sn_ref.pos()[1]**2)
            theta = np.arcsin(sn_ref.pos()[1]/r)
            load_n = load*r/Jy
            if sn_ref.pos()[0] < 0:
                load_n_final_x = sn_ref.apply()[0][0] + -load_n*np.sin(theta)
                load_n_final_y = sn_ref.apply()[0][1] + -load_n*np.cos(theta)
                sn_ref.set_apply(Type-5,load_n_final_x)
                sn_ref.set_apply(Type-4,load_n_final_y)
            else:
                load_n_final_x = sn_ref.apply()[0][0] + -load_n*np.sin(theta)
                load_n_final_y = sn_ref.apply()[0][1] +  load_n*np.cos(theta)
                sn_ref.set_apply(Type-5,load_n_final_x)
                sn_ref.set_apply(Type-4,load_n_final_y)

# loading('loading_ref', 1000, 0)
# loading('loading_ref', 1000, 1)
# loading('loading_ref', 1000, 2)
# loading('loading_ref', 1000, 5)

def ListIsZero(List):
    for i in range(len(List)):
        if List[i] == 0:
            return True
        else:
            return False

#def history(timestep_Foundation,interval,prj_dir):
def history2Convergence(*args):
    global prj_dir_his
    if it.cycle()%1000 == 0:
        it.command(f"history export 1 file '{prj_dir_his}/disp-x.his' truncate skip 200 vs step")
        it.command(f"history export 3 file '{prj_dir_his}/disp-z.his' truncate skip 200 vs step")
        it.command(f"history export 7 file '{prj_dir_his}/rotation.his' truncate skip 200 vs step")

def loading_procedure(soil_layers,pile_top,load_final,load_matrix_final,prj_dir):
    it.command(f"model restore '{prj_dir}\Foundation'")
    
    command ='''
    zone gridpoint initialize displacement 0.0 0.0 0.0
    zone gridpoint initialize velocity 0.0 0.0 0.0
    structure node initialize displacement 0.0 0.0 0.0
    structure node initialize displacement-rotational 0.0 0.0 0.0
    structure node initialize velocity 0.0 0.0 0.0
    structure node initialize velocity-rotational 0.0 0.0 0.0
    '''
    it.command(command)

    command = f'''
    structure node group 'loading_ref_1' slot 'reference' range position-z {pile_top} group 'MonoPile' slot 'Pile'
    structure node group 'loading_ref_2' slot 'reference' range position-z {soil_layers[0]} group 'MonoPile' slot 'Pile'
    structure node history displacement-x position 0 0 {soil_layers[0]}
    structure node history displacement-y position 0 0 {soil_layers[0]}
    structure node history displacement-z position 0 0 {soil_layers[0]}
    structure node history velocity-x position 0 0 {soil_layers[0]}
    structure node history velocity-y position 0 0 {soil_layers[0]}
    structure node history velocity-z position 0 0 {soil_layers[0]}
    '''
    it.command(command)
    
    command = f'''
    fish define rotation
        local sn_1 = struct.node.near( R,0,{soil_layers[0]})
        local sn_2 = struct.node.near(-R,0,{soil_layers[0]})
        local disp_z_1 = struct.node.disp.global(sn_1,3)
        local disp_z_2 = struct.node.disp.global(sn_2,3)
        local delta_z = math.abs(disp_z_1-disp_z_2)
        rotation = delta_z/(2*R)
    end
    
    fish history rotation
    '''
    it.command(command)
    
    it.command(f"model save '{prj_dir}\Temp'")
    
    for i in range(len(load_final)):
        if ListIsZero(load_final[i]) == False:
            it.command(f"model restore '{prj_dir}\Temp'")
            loading('loading_ref_1', load_final[i][0], 0)
            loading('loading_ref_1', load_final[i][1], 1)
            loading('loading_ref_1', load_final[i][2], 2)
            loading('loading_ref_1', load_final[i][3], 3)
            loading('loading_ref_1', load_final[i][4], 4)
            loading('loading_ref_1', load_final[i][5], 5)
            global prj_dir_his
            prj_dir_his = prj_dir
            it.set_callback(f"history2Convergence", -1)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(f"The loads are {load_final[i]}")
            it.command("model solve ratio 1e-6")
            #it.command("model solve ratio 1e-6 fish-call -1 history_update interval 1000")
            it.command(f"model save '{prj_dir}\{load_final[i][-1]}'")
            print(f"'{load_final[i][-1]}' saved!")
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    if ListIsZero(load_matrix_final) == False:
        for i in range(6):
            it.command(f"model restore '{prj_dir}\Temp'")
            loading('loading_ref_2', load_final[i], i)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(f"The load of comp-{i+1} is {load_final[i]}")
            it.command("model solve ratio 1e-6")
            it.command(f"model save '{prj_dir}\Matrix_{i}'")
            print(f"'Matrix_{i}' saved!")
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    os.remove(f"'{prj_dir}\Temp.sav'")