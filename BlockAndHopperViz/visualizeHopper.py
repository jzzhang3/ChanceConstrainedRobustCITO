import numpy as np
import os 
from utilities import load, FindResource  
from systems.visualization import Visualizer
from pydrake.all import PiecewisePolynomial, RigidTransform
from BlockAndHopperViz.visualizeBlockCore import weld_base_to_world, colors


def add_terrain(visualizer, terrain_color=None):
    # Add in the terrain and weld
    visualizer.addModelFromFile(FindResource("systems/urdf/blockterrain.urdf"))
    visualizer = weld_base_to_world(visualizer, visualizer.model_index[-1], np.array([-1, 0, 0]))
    if terrain_color is not None:
        terrain_inds = visualizer.plant.GetBodyIndices(visualizer.model_index[-1])
        for n in [0, 2]:
           visualizer.setBodyColor(terrain_inds[n], terrain_color)
    return visualizer

def set_hopper_colors(vis, model_index, color=np.array([1., 1., 1., 1.])):
    """Change the colors of all the links in the cart"""
    bodies = vis.plant.GetBodyIndices(model_index)
    for body in bodies[2:]:
        vis.setBodyColor(body, color)
    return vis

def visualize_multihopper(datasets, colors, terraincolor=None):
    """Visualize multiple carts at once"""
    nHoppers = len(datasets)
    # Create a cart visualizer
    hopperfile = "systems/hopper/urdf/footedhopper.urdf"
    visualizer = Visualizer(FindResource(hopperfile))
    for n in range(1, nHoppers):
        visualizer.addModelFromFile(FindResource(hopperfile), name="Hopper"+str(n))
    # Weld all carts to the world frame
    nX, nT = datasets[0]['xtraj'].shape
    xtraj = np.zeros((nX*nHoppers, nT))
    for n in range(nHoppers):
        # Weld the base and set color
        #visualizer = weld_base_to_world(visualizer, visualizer.model_index[n], translation=np.array([0., 2*n, 0.]))
        visualizer = weld_base_to_world(visualizer, visualizer.model_index[n], translation=np.array([0., 0.5*n, 0.]))
        visualizer = set_hopper_colors(visualizer, visualizer.model_index[n], colors[n])
        for k in range(nX):
            xtraj[n + k*nHoppers,:] = datasets[n]['xtraj'][k,:nT]
    # Add in the terrain and weld
    visualizer = add_terrain(visualizer, terraincolor)
    # Get the common time axis
    time = np.squeeze(datasets[0]['time'])
    # Create the trajectory
    traj = PiecewisePolynomial.FirstOrderHold(time, xtraj)
    # Visualize
    visualizer.visualize_trajectory(traj)

def main_matlab_erm():
    #TODO: Re-send the Hopper ERM data with Sigma variables attached
    ermdata = load("data/python_erm/HopperERM.pkl")
    nominal = load("data/python_erm/HopperNominal.pkl")
    print("Nominal starting position:")
    print(f"{nominal[0]['xtraj'][0:5,0]}")
    for data  in ermdata:
        print(f"ERM Sigma = {data['sigma']}")
        print("First configuration: x = ")
        print(f"{data['xtraj'][0:5,0]}")
    dataset = [nominal[0], ermdata[0], ermdata[1], ermdata[2]]
    colornames = ['blue', 'purple', 'yellow', 'red']
    datacolors = [colors[name] for name in colornames]
    # Visualize
    visualize_multihopper(dataset, datacolors)
    # Print out the sigma values and colors
    print(f"Visualized nominal in {colornames[0]}")
    for n in range(3):
        print(f"Visualized ERM with sigma = {ermdata[n]['sigma']} in {colornames[n+1]}")

def main_chance_erm():
    reffile = os.path.join("examples","hopper","reference_linear","strict_nocost")
    ermfile = os.path.join("examples","hopper","robust_nonlinear","decimeters_1e3","erm","success","nonlinear_NCC_sigma_5e+00_nochance")
    chancefile1 = os.path.join('examples','hopper','robust_nonlinear','decimeters_1e3','erm_cc',"success","nonlinear_NCC_sigma_5e+00_theta_7e-01_beta_5e-01")
    chancefile2 = os.path.join('examples','hopper','robust_nonlinear','decimeters_1e3','erm_cc',"success","nonlinear_NCC_sigma_5e+00_theta_6e-01_beta_5e-01")
    sources = [ermfile, chancefile1, chancefile2, reffile]
    dataset = [load(os.path.join(source, 'trajoptresults.pkl')) for source in sources]
    colornames = ['orange','brown', 'purple', 'blue']
    for n in range(len(dataset)):
        dataset[n]['xtraj'] = dataset[n]['state']
    datacolors = [colors[name] for name in colornames]

    # Visualize
    visualize_multihopper(dataset, datacolors)

if __name__ == "__main__":
    main_chance_erm()
