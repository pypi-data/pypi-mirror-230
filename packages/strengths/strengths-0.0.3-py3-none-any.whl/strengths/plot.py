import matplotlib.pyplot as plt
import matplotlib.colors as pltcol
from strengths.typechecking import *

"""
plotting utility
"""

def plot_trajectory (output, species, position=None) :
    """
    plots the time trajectory of one or more species. 
    
    It relies on the Matplotlib (Hunter, 2007) package [#matplotlib]_, 
    including matplotlib.pyplot.plot [#matplotlib_pyplot_plot]_.
    
    :param output: simulation output
    :type output: SimulationOutput
    :param species: labels of the species for which the trajectories should be plotted.
        if given a label, only one trajectory is plotted.
        if given an array, trajectories of all the labels are plotted.
    :param position: position of the mesh from which we want the trajectory. 
        if None, the global trajectory for the whole system is plotted instead.
    :type position: None, number, tuple or Coord like
    :type species: str or array of str.
    """
    
    merge = isnone(position)
    if merge : 
        position=0
    
    if type(species) == str :
        plt.title(species + " trajectory")
        plt.ylabel("species quantity (" + str(output.data.units) + ")")
        plt.xlabel("time (" + str(output.t.units) + ")")
        plt.plot(output.t.value, output.trajectory(species, merge=merge, position=position).value)
        plt.show()
    else :
        plt.title("species trajectories")
        plt.ylabel("species quantity (" + str(output.data.units) + ")")
        plt.xlabel("time (" + str(output.t.units) + ")")
        for s in species: 
            plt.plot(output.t.value, output.get_trajectory(s, merge=merge, position=position).value, label=s)
        plt.legend(loc="best")
        plt.show()
    
def plot_state_2D(output, species, sample, axis="auto", axis_position=0) : 
    """
    plots the distribution for the quantity of a species on a plan of the system space.
    
    It relies on the Matplotlib package (Hunter, 2007) [#matplotlib]_, 
    including matplotlib.pyplot.imshow [#matplotlib_pyplot_imshow]_.
    
    :param output: simulation output
    :type output: SimulationOutput   
    :param spacies: label of the species of which the state should be plotted
    :type species: str
    :param sample: index of the sample at chich the state should be taken
    :type sample: int
    :param axis: axis along which the state slice should be taken.
        accepted values are :
            
        * "auto" : the axis that seems the most appropriate is used
        * "x" : the x axis is taken 
        * "y" : the y axis used
        * "z" : the z axis is used
        
    :type axis: str
    :param axis_position: position of the slice along the slice axis
    :type axis_position: int
    """
    
    state = output.get_state(species, sample).value.reshape(
        output.system.space.d,
        output.system.space.h,
        output.system.space.w)
    
    if   axis == "auto" : 
        if   output.system.space.w == min(output.system.space.w, output.system.space.h, output.system.space.d) : axis = "x"
        elif output.system.space.h == min(output.system.space.w, output.system.space.h, output.system.space.d) : axis = "y"
        else :                                                                                                   axis = "z"
    
    if   axis == "x" : 
        plt.title(species+"\nx = "+str(axis_position)+" mesh"+"\nt = "+str(output.t.get_at(sample)))
        plt.xlabel("y (mesh)")
        plt.ylabel("z (mesh)")
        plt.imshow(state[:,:,axis_position])
        plt.colorbar(label="quantity "+str(output.data.units))
        plt.show()
    elif axis == "y" : 
        plt.title(species+"\ny = "+str(axis_position)+" mesh"+"\nt = "+str(output.t.get_at(sample)))
        plt.xlabel("x (mesh)")
        plt.ylabel("z (mesh)")
        plt.imshow(state[:,axis_position,:])
        plt.colorbar(label="quantity "+str(output.data.units))
        plt.show()
    elif axis == "z" : 
        plt.title(species+"\nz = "+str(axis_position)+" mesh"+"\nt = "+str(output.t.get_at(sample)))
        plt.xlabel("x (mesh)")
        plt.ylabel("y (mesh)")
        plt.imshow(state[axis_position,:,:])
        plt.colorbar(label="quantity ("+str(output.data.units)+")")
        plt.show()
    else : 
        raise ValueError(str(axis) + "is not an axxepted axis value. accepted value are \"x\", \"y\", \"z\" and \"auto\"" )
        
def plot_envmap_2D(system, axis="auto", axis_position=0, env_color_dict=None) : 
    """
    plots the distribution of the reaction diffusion environments on a plan of the system space.
    
    It relies on the Matplotlib package (Hunter, 2007) [#matplotlib]_, 
    including matplotlib.pyplot.imshow [#matplotlib_pyplot_imshow]_.
    
    :param system: reaction diffusion system
    :type system: RDSystem
    :param axis: axis along which the state slice should be taken.
        accepted values are :
            
        * "auto" : the axis that seems the most appropriate is used
        * "x" : the x axis is taken 
        * "y" : the y axis used
        * "z" : the z axis is used
        
    :type axis: str
    :param axis_position: position of the slice along the slice axis
    :type axis_position: int
    """
    
    envmap = system.space.mesh_env.reshape(
        system.space.d,
        system.space.h,
        system.space.w)
    
    colormap_colors = None
    n_env = system.network.nenvironments()
    
    if isdict(env_color_dict) : 
        colormap_colors = [env_color_dict[system.network.environments[i]] for i in range(n_env)]
    elif isarray(env_color_dict) : 
        colormap_colors = env_color_dict
    else:
        colormap_colors = [(i/n_env, i/n_env, i/n_env) for i in range(n_env)]
    
    colormap_ticks =        [i+0.5                          for i in range(n_env)]
    colormap_ticks_labels = [system.network.environments[i] for i in range(n_env)]
    colormap = pltcol.ListedColormap(colormap_colors)
    
    if   axis == "auto" : 
        if   system.space.w == min(system.space.w, system.space.h, system.space.d) : axis = "x"
        elif system.space.h == min(system.space.w, system.space.h, system.space.d) : axis = "y"
        else :                                                                       axis = "z"
    
    if   axis == "x" : 
        plt.title("environment map\nx = "+str(axis_position)+" mesh")
        plt.xlabel("y (mesh)")
        plt.ylabel("z (mesh)")
        plt.imshow(envmap[:,:,axis_position], cmap=colormap, vmax=n_env)
        plt.colorbar(ticks=colormap_ticks).set_ticklabels(colormap_ticks_labels)
        plt.show()
    elif axis == "y" : 
        plt.title("environment map\ny = "+str(axis_position)+" mesh")
        plt.xlabel("x (mesh)")
        plt.ylabel("z (mesh)")
        plt.imshow(envmap[:,axis_position,:], cmap=colormap, vmax=n_env)
        plt.colorbar(ticks=colormap_ticks).set_ticklabels(colormap_ticks_labels)
        plt.show()
    elif axis == "z" : 
        plt.title("environment map\nz = "+str(axis_position)+" mesh")
        plt.xlabel("x (mesh)")
        plt.ylabel("y (mesh)")
        plt.imshow(envmap[axis_position,:,:], cmap=colormap, vmax=n_env)
        plt.colorbar(ticks=colormap_ticks).set_ticklabels(colormap_ticks_labels)
        plt.show()
    else : 
        raise ValueError(str(axis) + "is not an accepted axis value. accepted value are \"x\", \"y\", \"z\" and \"auto\"" )

"""
References
----------

.. [#matplotlib] Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science \& Engineering, 9(3), 90-95. https://10.1109/MCSE.2007.55

.. [#matplotlib_pyplot_plot] The Matplotlib developpement team. matplotlib 3.7 API Reference : matplotlib.pyplot.plot. (consulted on september 05, 2023). https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html

.. [#matplotlib_pyplot_imshow]  The Matplotlib developpement team. matplotlib 3.7 API Reference : matplotlib.pyplot.imshow. (consulted on september 05, 2023). https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html
"""