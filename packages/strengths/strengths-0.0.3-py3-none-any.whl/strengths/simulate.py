import numpy as np
import copy as cpy
import random
import strengths
import strengths.simulation_interface_3D as i3D
from strengths.rdsystem import RDSystem
from strengths.units import *
from strengths import rdengine
from strengths import engine_collection
from strengths import filepath

"""
Module that contains the Simulate function, and related classes and functions.
"""

class SimulationOutput :
    """
    Store the output of a simulation.

    :param data: trajectory data [sample index, species index, mesh index]
    :type data: UnitArray with quantity units dimensions
    :param t_sample: sampling time points
    :type t_sample: UnitArray with time units dimensions
    :param system: reaction diffusion system associated with the trajectory
    :type system: RDSystem
    """

    def __init__ (self, data, t_sample, system):
        """
        constructor
        """

        self._data = data.copy()
        self._t = t_sample.copy()
        self._system = system.copy()

    @property
    def t(self) :
        """
        sampling times.
        """

        return self._t

    @property
    def data(self) :
        """
        array of sucessive sampled system states.
        """

        return self._data

    @property
    def w(self) :
        """
        system width in mesh.
        """

        return self.system.space.w

    @property
    def h(self) :
        """
        system height in mesh.
        """

        return self.system.space.h

    @property
    def d(self) :
        """
        system depth in mesh.
        """

        return self.system.space.d

    @property
    def species(self) :
        """
        list of species labels.
        the list ordered is the same than in the original rdnetwork and in the data.
        """

        return self.system.network.species_labels()

    @property
    def system(self) :
        """
        reaction diffusion system.
        """

        return self._system

    def nmeshes(self):
        """
        Returns the number of species.
        """

        return self.system.space.size()

    def nspecies(self) :
        """
        Returns the number of species.
        """

        return self.system.network.nspecies()

    def nsamples(self) :
        """
        Returns the number of samples.
        """

        return len(self.t)

    def get_trajectory(self, species, position=0, merge=False) :
        """
        Returns the trajectory of a given species. if merge=False, it is the trajectory at the given position,
        otherwise, it is the global trajectory in the whole system.

        :param species: species for which trajectory should be returned.
        :type species: Species, number or str
        :param position: position of the mesh in which the trajectory should be taken.
            it is ignored if merge=True.
        :type position: number, tuple or Coord like.
        :param merge: if True, position is ignored, and the global trajectory of the species is trturned.
        :type merge: bool
        :returns: local ot global trajectory of the species.
        :rtype: UnitArray of quantity units dimensions
        """

        species_index = self.system.network.get_species_index(species)
        if isnone(species_index) :
            raise Exception("Undefined species \""+species+"\".")

        mesh_index = self.system.space.get_mesh_index(position)

        if not merge :
            return UnitArray(self.data.value.reshape((self.nsamples(), self.nspecies(), self.nmeshes()))[:,species_index, position], self.data.units, check_value=False)
        else : #merge
            return UnitArray([sum(state) for state in self.data.value.reshape((self.nsamples(), self.nspecies(), self.nmeshes()))[:,species_index, :]], self.data.units, check_value=False)

    def get_state(self, species, sample) :
        """
        Returns the state of a given species at a given sample index.

        :param species: species, species label or species index
        :type species: Species, int or str
        :param sample: sample index
        :type sample: int
        :returns: sampled species state at the given sample index.
        """

        species_index = self.system.network.get_species_index(species)
        if isnone(species_index) :
            raise Exception("Undefined species \""+species+"\".")

        sample_index = sample

        return UnitArray(
            self.data.value.reshape((self.nsamples(), self.nspecies(), self.nmeshes()))[sample_index, species_index, :], self.data.units, check_value=False)

    def get_trajectory_point(self, species, sample, position) :
        """
        Returns the value of a given species trajectory, at a given sample, at a given position.

        :param species: species, species label or index
        :type species: Species, int or str
        :param sample: sample index
        :type sample: int
        :param position: position in the mesh space.
            can be a linear index (int) or a class with x,y,z properties/members representing spatial cooridnates in a MeghGrid.
        :returns: sample value at the given position for the given species (number).
        """

        species_index = self.system.network.get_species_index(species)
        if isnone(species_index) :
            raise Exception("Undefined species \""+species+"\".")

        mesh_index = self.system.space.get_mesh_index(position)

        sample_index = sample

        return self.data[sample_index*self.nspecies()*self.nmeshes() + species_index*self.nmeshes() + mesh_index]

def save_simulationoutput(so, path, separate_data=True) :
    """
    Saves a simulation output as a file.

    :param so: simulation output to be saved.
    :type so: SimulationOutput
    :param path: path of the output file to be created or replaced.
        the .json extension suffix is added if absent.
    :type path: str
    :param separate_data: specifies if the data should be saved in a separate file.
        if true, the trajectory data are saved in a different file using the numpy.save function [#numpy_save]_.
        This makes the saving and loading faster, especially for large simulation outputs.
        if filename.json is the name of the json file,
        the data are saved as filename_data.npy (NPY format [#numpy_npy]_).
    :type separate_data: bool
    """
    # references :
    # .. [#numpy_save] Numpy Developers. numpy 1.25 API reference : numpy.save. (consulted on september 05, 2023). https://numpy.org/doc/stable/reference/generated/numpy.save.html#numpy.save
    # .. [#numpy_npy] Numpy Developers. numpy 1.25 API reference : numpy.lib.format # NPY format. (consulted on september 05, 2023). https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#npy-format

    json_path = filepath.append_extension_if_missing(path, ".json")
    data_path = filepath.remove_extension_if_existing(path, ".json") + "_data.npy"

    if separate_data :
        d = {
            "system" : rdsystem_to_dict(so.system),
            "data_units" : str(so.data.units),
            "t_sample" : unitarray_to_dict(so.t)
            }

        f = open(json_path, "w", encoding="utf-8")
        json.dump(d, f, indent = 4)

        np.save(data_path, so.data.value)

    else :
        d = {
            "system" : rdsystem_to_dict(so.system),
            "data" : unitarray_to_dict(so.data),
            "t_sample" : unitarray_to_dict(so.t)
            }

        f = open(json_path, "w", encoding="utf-8")
        json.dump(d, f, indent = 4)

def load_simulationoutput(path) :
    """
    Load a simulation output from a file.

    :param path: path of the output file to be created or replaced.
    :type path: str
    :return: loaded simulation output.
    :rtype: SimulationOutput
    """

    f = open(path, "r", encoding="utf-8")
    d = json.load(f)

    system = rdsystem_from_dict(d["system"])

    if not isnone(d.get("data", None)) :
        data = unitarray_from_dict(d["data"])
    else :
        data = UnitArray(
            value = np.load(filepath.remove_extension_if_existing(path, ".json") + "_data.npy"),
            units = d["data_units"])

    t_sample = unitarray_from_dict(d["t_sample"])

    return SimulationOutput(data, t_sample, system)

def simulate(
        system,
        t_sample,
        time_step="0.01 s",
        engine = engine_collection.euler_engine(),
        seed=None,
        units_system=UnitsSystem(),
        print_progress=False
        ) :
    """
    Simulates the evolution in time of a reaction diffusion system.

    :param system: reaction diffusion system at its initial state.
    :type system: System
    :param t_sample: time points at which the system state is sampled during the simulation.
    :type t_sample: array of numbers or UnitArray
    :param engine: Reference to the engine that should be used to perform the simulation.
        see the documentation or the engine_collection submodule for more information
        on the engines preinstalled with strengths. (default = engine_collection.euler)
    :type engine: a RDEngineReferenceBase derived class (ie. LibRDEngineReference)
    :param seed: pseudo random number generator seed.
    :type seed: int
    :param time_step: time step, used when necessary.
    :type time_step: number, str or UnitValue
    :param units_system: default units system
    :type units_system: UnitsSystem
    :param print_progress: if true, the progression of the simulation (percentage) is printed
        at frequently.
    :type print_progress: bool
    :return: trajectory of the system sampled at **t_sample**
    :rtype: SimulationOutput
    """

    # #####################################################################
    # argument checking and processing

    # units_system (must be checked first, as it is involved checking/processings)
    if type(units_system) == dict :
        units_system = unitssystem_from_dict(units_system)
    elif type(units_system) == UnitsSystem :
        units_system = units_system.copy()
    else :
        raise ValueError("units_system must be a dict or an instance of UnitsSystem.")

    # t_sample
    if isarray(t_sample) :
        t_sample = UnitArray(t_sample, Units(units_system, time_units_dimensions()))
    elif type(t_sample) == UnitArray :
        t_sample = t_sample.copy()
    else :
        raise ValueError("t_sample must be an array or a UnitArray")

    if t_sample.units.dim != time_units_dimensions() :
        raise ValueError("t_sample units must be time.")

    # time_step
    if isnumber(time_step) :
        time_step = UnitValue(time_step, Units(units_system, time_units_dimensions()))
    elif type(time_step) == str :
        time_step = parse_unitvalue(time_step)
    elif type(time_step) == UnitValue :
        time_step = time_step.copy()
    else :
        raise ValueError("time step must be a number, a string or a UnitValue.")

    if time_step.units.dim != time_units_dimensions() :
        raise ValueError("time step units must be time.")

    # system
    if type(system) != RDSystem :
        raise ValueError("system must be a RDSystem.")
    system = system.copy()

    # seed
    if seed == None :
        seed = random.randint(0, (2**32)-1)
    else :
        seed = int(seed)

    # engine
    if not issubclass(type(engine), rdengine.RDEngineReferenceBase) :
        raise ValueError("engine must be a EngineReferenceBase derived object.")

    # #####################################################################

    species = [s.label for s in system.network.species]

    result, out_t_sample = i3D.simulate_3D(
        system = system,
        t_sample = t_sample,
        time_step = time_step,
        engine_reference = engine,
        seed = seed,
        units_system = units_system,
        print_progress=print_progress
        )

    return SimulationOutput(result, out_t_sample, system)
