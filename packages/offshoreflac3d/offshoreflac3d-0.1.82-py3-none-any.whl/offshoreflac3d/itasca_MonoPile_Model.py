import numpy as np 
import itasca as it
import os
it.command("python-reset-state false")

#
def model(R,L,pile_top,scour_depth,soil_layers,prj_dir):
    layering = []
    for i in soil_layers:
        layering.append(i)
    layering.append(soil_layers[0]-scour_depth)
    layering.append(soil_layers[0]-L)
    layering.append(pile_top)
    layering.sort(reverse=True)
    # print(layering)
    #model new#########################
    it.command("model new")
    it.fish.set('R',R)
    it.fish.set('mudline',soil_layers[0])
    it.fish.set('scour_depth',scour_depth)
    it.fish.set('boundary_z',soil_layers[-1])
    #basic model
    command1 = f'''zone import '{prj_dir}/zone_{int(R)}.inp' format abaqus
    zone group 'SC' slot 'suction caisson'
    '''
    it.command(command1)

    # for gp in it.gridpoint.list():
        # gp.set_pos_x(gp.pos_x()+distance/2)
        # gp.set_pos_y(gp.pos_y()+distance/2)
    
    command = '''
    zone reflect origin 0 0 0 normal 0 1 0 merge on
    zone reflect origin 0 0 0 normal 1 0 0 merge on
    '''
    it.command(command)
    #layering
    for gp in it.gridpoint.list():
        gp.set_pos_z(gp.pos_z()+layering[0]-0.1)

    command_template = ("zone copy 0 0 {} merge on range position-z {} {}")

    for i in layering:
        if i == layering[0]:
            continue
        elif i == layering[-1]:
            continue
        else:
            it.command(command_template.format(i-layering[0],layering[0],layering[1]))
        
    for gp in it.gridpoint.list():    
        for i in range(len(layering)-1):
            #if round(gp.pos_z()) == round(layering[i]):
            if gp.pos_z() > layering[i]-0.1-0.05 and gp.pos_z() < layering[i]-0.1+0.05:
                # print(layering[i+1])
                gp.set_pos_z(layering[i+1])

    # print(soil_layers)
      
    for z in it.zone.list():
        for i in range(len(soil_layers)-1):
            if z.pos_z() <= soil_layers[i] and z.pos_z() >= soil_layers[i+1]:
                z.set_group("soil_{}".format(i),"soil")

    for i in range(len(layering)-1):
        if layering[i]-layering[i+1] <= 0.5:
            continue
        elif layering[i]-layering[i+1] > 0.5 and layering[i]-layering[i+1] < 1.0:
            it.command("zone densify global segments 1 1 2 range position-z {} {}".format(layering[i],layering[i+1]))
        else:
            if layering[0]-L < layering[i+1]:
                command = "zone densify global segments 1 1 {} range position-z {} {}"
                it.command(command.format(int(layering[i]-layering[i+1])*2,layering[i],layering[i+1]))
            else:
                command = "zone densify global segments 1 1 {} range position-z {} {}"
                it.command(command.format((int(layering[i]-layering[i+1])+1)*1,layering[i],layering[i+1]))

    it.command("zone densify global segments 1 1 2")
    it.command("zone attach by-face tolerance-absolute 0.1")
    it.command(f"model save '{prj_dir}/Model'")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("'Model' saved!")
    print("basic information for checking!")
    print(f"Diameter = {R*2}; Embedded_Length = {L}")
    print(f"original soil layers: {soil_layers}")
    print(f"original model layers: {layering}")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    os.remove(f"{prj_dir}\zone_{int(R)}.inp")





























