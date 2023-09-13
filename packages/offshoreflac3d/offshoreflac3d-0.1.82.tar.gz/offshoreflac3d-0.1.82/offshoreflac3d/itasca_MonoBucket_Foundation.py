import numpy as np
import itasca as it
it.command("python-reset-state false")

def foundation(soil_layers,L,scour_depth,bucket_prop,bucket_density,thickness,coupling_prop_1,coupling_prop_2,bulk,shear,prj_dir):
    it.command(f"model restore '{prj_dir}\Initial'")
    
    for z in it.zone.list():
        groups = ['Volume1','Volume2','Volume3']
        for group in groups:
            if z.in_group(group):
                z.set_group('suction caisson','SC')
    
        groups = ['Volume4','Volume5','Volume6','Volume7','Volume8','Volume9','Volume10','Volume11']
        for group in groups:
            if z.in_group(group):
                z.set_group('NoSC','SC')
    
    
    command = f'''
    structure liner create by-zone-face id 11 group 'Cap' slot 'SC' element-type=dkt-cst range position-z {soil_layers[0]} group 'suction caisson' slot 'SC'
    zone face group 'InterFace' slot '1' internal range group 'NoSC' slot 'SC' group 'suction caisson' slot 'SC' position-z {soil_layers[0]-L} {soil_layers[0]}
    zone separate by-face new-side group 'InterFace2' range group 'InterFace' slot '1'
    structure liner create by-face id 11 group 'Skirt' slot 'SC' element-type=dkt-cst embedded range group 'InterFace2'
    
    structure liner group 'bucket' range group 'Skirt' slot 'SC'
    structure liner group 'bucket' range group 'Cap' slot 'SC'
    '''
    it.command(command)
    
    command = f'''
    structure liner property isotropic {bucket_prop[0]} {bucket_prop[1]}
    structure liner property density {bucket_density[1]} thickness {thickness[1]} range group 'Skirt' slot 'SC'
    structure liner property density {bucket_density[0]} thickness {thickness[0]} range group 'Cap' slot 'SC'
    structure node join
    '''
    it.command(command)
    
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
    print("basic information for checking!")
    print(f"Cap properties: density = {bucket_density[0]}, thickness = {thickness[0]}, isotropic = {bucket_prop[0]} {bucket_prop[1]}")
    print(f"Skirt properties: density = {bucket_density[1]}, thickness = {thickness[1]}, isotropic = {bucket_prop[0]} {bucket_prop[1]}")
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

