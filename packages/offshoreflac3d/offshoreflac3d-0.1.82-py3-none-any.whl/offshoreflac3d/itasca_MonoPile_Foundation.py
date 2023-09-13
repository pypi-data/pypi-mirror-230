import numpy as np 
import itasca as it
it.command("python-reset-state false")


def foundation(soil_layers,embbedded_length,pile_prop,pile_density,thickness,scour_depth,radius,radius_2,VariableRange,bulk,shear,coupling_prop_1,coupling_prop_2,prj_dir):
    
    it.command(f"model restore '{prj_dir}/Initial.sav'")
    
    for z in it.zone.list():
        groups = ['Volume1','Volume2','Volume3']
        for group in groups:
            if z.in_group(group):
                z.set_group('MonoPile','Pile')
    
        groups = ['Volume4','Volume5','Volume6','Volume7','Volume8','Volume9','Volume10','Volume11']
        for group in groups:
            if z.in_group(group):
                z.set_group('NoPile','Pile')
    
        # groups = ['Volume4','Volume5']
        # for group in groups:
            # if z.in_group(group):
                # z.set_group('Concrete','SC')

    # command = '''
    # zone cmodel assign elastic range group "Concrete" slot "SC" position-z {} {}
    # zone property density 25.0 young 3.8e6 poisson 0.2 range cmodel 'elastic'
    # '''
    # it.command(command.format(soil_layers[0],soil_layers[0]-L))
    
    if VariableRange[1] < soil_layers[0]:
        geometry_warning = "!!!!!!!!!!!!!!!the varied section is in soil!!!!!!!!!!!!!!!"
    
    if len(VariableRange) > 0:
        for gp in it.gridpoint.list():
            if gp.pos()[2] >= VariableRange[1] and gp.pos()[2] <= VariableRange[0]:
                n = (gp.pos()[2]-VariableRange[1])/(VariableRange[0]-VariableRange[1])
                gp.set_pos_x(gp.pos()[0] * (radius + (radius_2-radius)* n)/ radius)
                gp.set_pos_y(gp.pos()[1] * (radius + (radius_2-radius)* n)/ radius)
            elif gp.pos()[2] > VariableRange[0]:
                gp.set_pos_x(gp.pos()[0] * radius_2 / radius)
                gp.set_pos_y(gp.pos()[1] * radius_2 / radius)

    command = f'''
    zone cmodel assign elastic range position-z {soil_layers[0]} 1000
    zone face group 'InterFace' slot '1' internal range group 'NoPile' slot 'Pile' group 'MonoPile' slot 'Pile' position-z 1000 {soil_layers[0]-embbedded_length}
    zone separate by-face new-side group 'InterFace2' range group 'InterFace' slot '1'
    structure liner create by-face id 11 group 'MonoPile' slot 'Pile' element-type=dkt-cst embedded range group 'InterFace2'
    
    structure liner property coupling-stiffness-normal 2e8 coupling-stiffness-shear 2e8 coupling-yield-normal 1e6 coupling-cohesion-shear 2.5e3 coupling-friction-shear 50
    zone delete range position-z {soil_layers[0]} 1000
    '''
    it.command(command)
    
    
    command = f'''
    structure liner property isotropic {pile_prop[0]} {pile_prop[1]}
    structure liner property density {pile_density}
    structure node join
    '''
    it.command(command)
    
    thick, t_range = thickness
    
    for se in it.structure.list():
        for i in range(len(t_range)-1):
            if se.pos()[2] < t_range[i] and se.pos()[2] > t_range[i+1]:
                se.set_thickness(thick[i])
    
    
    for i in range(len(coupling_prop_2[0])):
        if i == 0:
            if coupling_prop_1[0][i] == 0:
                command = f'''
                structure liner property coupling-stiffness-normal {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-normal-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-yield-normal {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-yield-normal-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-shear {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-shear-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-cohesion-shear {coupling_prop_2[0][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-cohesion-shear-2 {coupling_prop_2[1][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-friction-shear {coupling_prop_2[2][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-friction-shear-2 {coupling_prop_2[3][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                '''
            else:
                command = f'''
                structure liner property coupling-stiffness-normal {coupling_prop_1[0][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-normal-2 {coupling_prop_1[1][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-yield-normal {coupling_prop_1[0][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-yield-normal-2 {coupling_prop_1[1][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-shear {coupling_prop_1[2][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-stiffness-shear-2 {coupling_prop_1[3][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-cohesion-shear {coupling_prop_2[0][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-cohesion-shear-2 {coupling_prop_2[1][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-friction-shear {coupling_prop_2[2][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                structure liner property coupling-friction-shear-2 {coupling_prop_2[3][i]} range position-z {soil_layers[0]+0.1} {soil_layers[1]} 
                '''
        else:
            if coupling_prop_1[0][i] == 0:
                command = f'''
                structure liner property coupling-stiffness-normal {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-stiffness-normal-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-yield-normal {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-yield-normal-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-stiffness-shear {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-stiffness-shear-2 {(bulk[i]+4/3*shear[i])/0.5} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-cohesion-shear {coupling_prop_2[0][i]} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-cohesion-shear-2 {coupling_prop_2[1][i]} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-friction-shear {coupling_prop_2[2][i]} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-friction-shear-2 {coupling_prop_2[3][i]} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                '''
            else:
                command = f'''
                structure liner property coupling-stiffness-normal {coupling_prop_1[0][i]} range position-z {soil_layers[i]} {soil_layers[i+1]} 
                structure liner property coupling-stiffness-normal-2 {coupling_prop_1[1][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-yield-normal {coupling_prop_1[0][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-yield-normal-2 {coupling_prop_1[1][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-stiffness-shear {coupling_prop_1[2][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-stiffness-shear-2 {coupling_prop_1[3][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-cohesion-shear {coupling_prop_2[0][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-cohesion-shear-2 {coupling_prop_2[1][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-friction-shear {coupling_prop_2[2][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                structure liner property coupling-friction-shear-2 {coupling_prop_2[3][i]} range position-z {soil_layers[i]} {soil_layers[i+1]}
                '''
        it.command(command)
    
    command ='''
    structure liner property slide off
    '''
    it.command(command)
    
    if scour_depth == 0:
        pass
    else:
        it.command(f"zone delete range position-z {soil_layers[0]} {soil_layers[0]-scour_depth} group 'suction caisson' slot 'SC' not")
        print("+++++++++++++++++++++ A scour is considered!")
    
    
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        print(geometry_warning)
    except:
        pass
    print("basic information for checking!")
    print(f"Pile properties: density = {pile_density}, thickness = varied, isotropic = {pile_prop[0]} {pile_prop[1]}")
    for i in range(len(coupling_prop_2[0])):
        if coupling_prop_1[0][i] == 0:
            print("------------------")
            print(f"The coupling properties are default values!")
            print(f"The coupling properties in layer {i+1}:")
            print(f"Coupling normal stiffness = Coupling shear stiffness = {(bulk[i]+4/3*shear[i])/0.5}")
            print(f"Coupling cohesion = {coupling_prop_2[0][i]}")
            print(f"Coupling friction = {coupling_prop_2[2][i]}")
        else:
            print("------------------")
            print(f"The coupling properties are user-defined!")
            print(f"The coupling properties in layer {i+1}:")
            print(f"Coupling normal stiffness = Coupling shear stiffness = {coupling_prop_1[0][i]}")
            print(f"Coupling cohesion = {coupling_prop_2[0][i]}")
            print(f"Coupling friction = {coupling_prop_2[2][i]}")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    
    it.command("model solve ratio 1e-6")
    it.command(f"model save '{prj_dir}\Foundation.sav'")
    print("'Foundation' saved!")


    



