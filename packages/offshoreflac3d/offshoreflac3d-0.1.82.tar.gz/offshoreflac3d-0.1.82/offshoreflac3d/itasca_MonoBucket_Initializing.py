import numpy as np 
from shapely import geometry as geo
import itasca as it
it.command("python-reset-state false")



def initializing(R_max,soil_layers,density,elastic,poisson,cohesion,friction,prj_dir):
    bulk = []
    shear = []
    for i in range(len(density)):
        bulk.append(elastic[i] / (3.0 * (1.0 - 2.0 * poisson[i])))
        shear.append(elastic[i] / (2.0 * (1.0 + poisson[i])))

    it.command(f"model restore '{prj_dir}\Model'")
    it.command("model gravity 9.8")
    it.command("model large-strain off")
    it.command("zone cmodel m-c")

    # print("printing materical properties")
    # print(density)
    # print(elastic)
    # print(poisson)
    # print(cohesion)
    # print(friction)

    for i in range(len(density)):
        command1 = "zone property density {} range group 'soil_{}' slot 'soil'"
        command2 = "zone property shear {} bulk {} cohesion {} friction {} tension 1e3 range group 'soil_{}' slot 'soil'"
        command3 = "zone initialize-stresses ratio {} range group 'soil_{}' slot 'soil'"
        it.command(command1.format(density[i],i))
        it.command(command2.format(shear[i],bulk[i],cohesion[i],friction[i],i))
        it.command(command3.format(poisson[i]/(1-poisson[i]),i))
        print("+++++++++++++++++++++ Assigning properties in soil_{} finished!".format(i))

    #it.command("zone initialize-stresses ratio 0.85 range group 'soil_3' slot 'soil'")

    for gp in it.gridpoint.list():
        pos_x = gp.pos_x()
        pos_y = gp.pos_y()
        r_dist = pos_x*pos_x + pos_y*pos_y
        if gp.pos_z() == soil_layers[-1]:
            gp.set_fix(0,True)
            gp.set_fix(1,True)
            gp.set_fix(2,True)
        elif r_dist > R_max**2-0.1 and r_dist < R_max**2+0.1:
            gp.set_fix(0,True)
            gp.set_fix(1,True)

    print("+++++++++++++++++++++ Boundary conditions assigned!")

    it.command("model solve ratio 1e-6")
    it.command(f"model save '{prj_dir}\Initial'")
    
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("'Initial' saved!")
    print("basic information for checking!")
    print(f"density [t/m3] = {density}")
    print(f"young modulus [MPa] = {elastic}")
    print(f"poisson ratio [-] = {poisson}")
    print(f"cohesion [kPa] = {cohesion}")
    print(f"friction [degree] = {friction}")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")

