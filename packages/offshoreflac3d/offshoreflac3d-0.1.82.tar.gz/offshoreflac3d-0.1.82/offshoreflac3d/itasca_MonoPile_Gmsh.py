import numpy as np 
import gmsh
import os

def main(R,List_R,prj_dir):
    num_zone = 8
    gmsh.initialize()

    # alias to facilitate code writing
    factory = gmsh.model.geo

    # default mesh size (not necessary, since we are using transfinite curves
    # and setting a certain number of points in all curves)
    lc = 1.0
    angle = np.pi/4.
    # Geometry
    # points
    p1 = factory.addPoint(0., 0., 0., lc)
    p2 = factory.addPoint(R, 0., 0., lc)
    p3 = factory.addPoint(0., R, 0., lc)
    p4 = factory.addPoint(R/3, 0., 0., lc)
    p5 = factory.addPoint(0., R/3, 0., lc)
    p6 = factory.addPoint(R/3, R/3, 0., lc)
    p7 = factory.addPoint(R*np.cos(angle), R*np.sin(angle), 0., lc)
    p8 = factory.addPoint(List_R[0], 0., 0., lc)
    p9 = factory.addPoint(0. ,List_R[0], 0., lc)
    p10 = factory.addPoint(List_R[0]*np.cos(angle), List_R[0]*np.sin(angle), 0., lc)
    p11 = factory.addPoint(List_R[1], 0., 0., lc)
    p12 = factory.addPoint(0. ,List_R[1], 0., lc)
    p13 = factory.addPoint(List_R[1]*np.cos(angle), List_R[1]*np.sin(angle), 0., lc)
    p14 = factory.addPoint(List_R[2], 0., 0., lc)
    p15 = factory.addPoint(0. ,List_R[2], 0., lc)
    p16 = factory.addPoint(List_R[2]*np.cos(angle), List_R[2]*np.sin(angle), 0., lc)
    p17 = factory.addPoint(List_R[3], 0., 0., lc)
    p18 = factory.addPoint(0. ,List_R[3], 0., lc)
    p19 = factory.addPoint(List_R[3]*np.cos(angle), List_R[3]*np.sin(angle), 0., lc)


    # lines
    l1 = factory.addLine(p5, p6)
    l2 = factory.addLine(p6, p4)
    l3 = factory.addLine(p4, p1)
    l4 = factory.addLine(p1, p5)
    l5 = factory.addLine(p4, p2)
    l6 = factory.addLine(p5, p3)
    l7 = factory.addLine(p6, p7)
    l8 = factory.addCircleArc(p2, p1, p7)
    l9 = factory.addCircleArc(p7, p1, p3)
    l10 = factory.addLine(p2, p8)
    l11 = factory.addCircleArc(p8, p1, p10)
    l12 = factory.addCircleArc(p10, p1, p9)
    l13 = factory.addLine(p3, p9)
    l14 = factory.addLine(p7, p10)
    l15 = factory.addCircleArc(p12, p1, p13)
    l16 = factory.addCircleArc(p11, p1, p13)
    l17 = factory.addLine(p8, p11)
    l18 = factory.addLine(p10, p13)
    l19 = factory.addLine(p9, p12)
    l20 = factory.addCircleArc(p15, p1, p16)
    l21 = factory.addCircleArc(p14, p1, p16)
    l22 = factory.addLine(p11, p14)
    l23 = factory.addLine(p13, p16)
    l24 = factory.addLine(p12, p15)
    l25 = factory.addCircleArc(p18, p1, p19)
    l26 = factory.addCircleArc(p17, p1, p19)
    l27 = factory.addLine(p14, p17)
    l28 = factory.addLine(p16, p19)
    l29 = factory.addLine(p15, p18)

    # curve loops
    cl1 = factory.addCurveLoop([l3, l4, l1, l2])
    cl2 = factory.addCurveLoop([l7, l9, -l6, l1])
    cl3 = factory.addCurveLoop([l5, l8, -l7, l2])
    cl4 = factory.addCurveLoop([l10, l11, -l14, -l8])
    cl5 = factory.addCurveLoop([l13, -l12, -l14, l9])
    cl6 = factory.addCurveLoop([l17, l16, -l18, -l11])
    cl7 = factory.addCurveLoop([l19, l15, -l18, l12])
    cl8 = factory.addCurveLoop([l22, l21, -l23, -l16])
    cl9 = factory.addCurveLoop([l24, l20, -l23, -l15])
    c20 = factory.addCurveLoop([l27, l26, -l28, -l21])
    c21 = factory.addCurveLoop([l29, l25, -l28, -l20])

    # surfaces
    s1 = factory.addPlaneSurface([cl1])
    s2 = factory.addPlaneSurface([cl2])
    s3 = factory.addPlaneSurface([cl3])
    s4 = factory.addPlaneSurface([cl4])
    s5 = factory.addPlaneSurface([cl5])
    s6 = factory.addPlaneSurface([cl6])
    s7 = factory.addPlaneSurface([cl7])
    s8 = factory.addPlaneSurface([cl8])
    s9 = factory.addPlaneSurface([cl9])
    s10 = factory.addPlaneSurface([c20])
    s11 = factory.addPlaneSurface([c21])

    # extrusions
    dx = 0.1
    num_els_z = 1
    factory.extrude([(2, s1), (2, s2), (2, s3), (2, s4), (2, s5), (2, s6), (2, s7), (2, s8), (2, s9), (2, s10), (2, s11)], 0., 0., dx,
                    numElements=[num_els_z], recombine=True)

    factory.synchronize()

    # Meshing
    meshFact = gmsh.model.mesh

    # transfinite curves
    n_nodes = num_zone+1
    # "Progression" 1 is default
    meshFact.setTransfiniteCurve(l1, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l2, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l3, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l4, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l5, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l6, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l7, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l8, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l9, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l10, numNodes=n_nodes-3)
    meshFact.setTransfiniteCurve(l11, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l12, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l13, numNodes=n_nodes-3)
    meshFact.setTransfiniteCurve(l14, numNodes=n_nodes-3)
    meshFact.setTransfiniteCurve(l15, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l16, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l17, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l18, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l19, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l20, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l21, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l22, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l23, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l24, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l25, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l26, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l27, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l28, numNodes=n_nodes)
    meshFact.setTransfiniteCurve(l29, numNodes=n_nodes)
    # transfinite surfaces
    meshFact.setTransfiniteSurface(s1)
    meshFact.setTransfiniteSurface(s2)
    meshFact.setTransfiniteSurface(s3)
    meshFact.setTransfiniteSurface(s4)
    meshFact.setTransfiniteSurface(s5)
    meshFact.setTransfiniteSurface(s6)
    meshFact.setTransfiniteSurface(s7)
    meshFact.setTransfiniteSurface(s8)
    meshFact.setTransfiniteSurface(s9)
    meshFact.setTransfiniteSurface(s10)
    meshFact.setTransfiniteSurface(s11)

    # mesh
    meshFact.generate(2)
    meshFact.recombine()
    meshFact.generate(3)
    
    gmsh.write('''{}\zone_{}.inp'''.format(prj_dir,int(R)))
    

    #gmsh.fltk.run()

    gmsh.finalize()
    
