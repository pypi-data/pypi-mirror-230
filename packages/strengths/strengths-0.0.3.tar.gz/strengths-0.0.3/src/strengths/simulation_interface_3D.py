import ctypes
import numpy as np
from strengths.typechecking import *
from strengths.units import *

"""
Module that contains the implementation of the simulate function for simulations in 3D mesh grids.
"""

def build_reaction_rate_constant_array(reactions, units_system) :
    """
    return the array of the forward reaction rate constants numerical values.

    :param reactions: array of irreversible forward reactions.
    :type reactions: array of Reaction
    :param units_system: units_system in which the rates should be expressed.
    :type units_system: UnitsSystem
    :rtype: array of int
    """

    return [r.kf.convert(units_system).value for r in reactions]

def build_reaction_environment_boolean_matrix(reactions, environments) :
    """
    return reaction environment boolean matrix in linear form.
    let *m* be such a *n_reactions*x*n_environments* matrix. *r* reffer to a reaction (row), and *e* refer to an environment (column).
    *m_{r,e} = 1*, if reaction *j* can happend in environment *i*, *0* otherwise.
    the linear form is *[m_{0,0},m_{0,1},... m_{0,n_environments},m_{1,0}, ..., m_{n_reactions,n_environments}]*.

    :param reactions: array of irreversible forward reactions.
    :type reactions: array of Reaction
    :param environments: array of environment labels.
    :type environments: array of str
    :rtype: array of int
    """

    nr = len(reactions)
    ne = len(environments)
    r_env = np.zeros(nr*ne, dtype=int)
    for r in range(nr) :
        for e in range(ne) :
            if reactions[r].environments == None :
                r_env[r * ne + e] = 1
            else :
                r_env[r * ne + e] = int(environments[e] in reactions[r].environments)
    return r_env

def build_substrate_stoechiometric_matrix(species, reactions) :
    """
    return substrate stoechiometric matrix in linear form.
    let *m* be such a *n_species*x*n_reactions* matrix. *s* reffer to a species (row), and *r* to a reaction (column).
    *m_{s,r}* is the stoechiometric coefficent associated with *s* in the substrate side of reaction *r*.
    the linear form is *[m_{0,0},m_{0,1},... m_{0,n_reactions},m_{1,0}, ..., m_{n_species,n_reactions}]*.

    :param species: array of species.
    :type species: array of Species
    :param reactions: array of irreversible forward reactions.
    :type reactions: array of Reaction
    :rtype: array of int
    """

    n_species   = len(species)
    n_reactions = len(reactions)
    species_labels = [s.label for s in species]
    sub = np.zeros(n_species*n_reactions, dtype=int)
    for s in range(n_species):
        for r in range(n_reactions):
            sub[s*n_reactions+r] = reactions[r].ssto(species_labels)[s]
    return sub

def build_stoechiometric_difference_matrix(species, reactions) :
    """
    return stoechiometric difference matrix in linear form.
    let *m* be such a *n_species*x*n_reactions* matrix. *s* reffer to a species (row), and *r* to a reaction (column).
    *m_{s,r}* is the difference of stoechiometric coefficent (products-substrates) for species *s* in reaction *r*.
    the linear form is *[m_{0,0},m_{0,1},... m_{0,n_reactions},m_{1,0}, ..., m_{n_species,n_reactions}]*.

    :param species: array of species.
    :type species: array of Species
    :param reactions: array of irreversible forward reactions.
    :type reactions: array of Reaction
    :rtype: array of int
    """

    n_species   = len(species)
    n_reactions = len(reactions)
    species_labels = [s.label for s in species]
    sto = np.zeros(n_species*n_reactions, dtype=int)
    for s in range(n_species):
        for r in range(n_reactions):
            sto[s*n_reactions+r] = reactions[r].dsto(species_labels)[s]
    return sto

def build_diff_coef_environment_matrix(species, environments, units_system) :
    """
    return the species diffusion coefficient matrix in linear form.
    let *m* be such a *n_species*x*n_environments* matrix. *s* reffer to a species (row), and *e* refer to an environment (column).
    *m_{s,e}* is the diffusion coefficent of species *s* in the enviroment *e*.
    the linear form is *[m_{0,0},m_{0,1},... m_{0,n_environments},m_{1,0}, ..., m_{n_species,n_environments}]*.

    :param species: array of species.
    :type species: array of Species
    :param environments: array of environment labels.
    :type environments: array of str
    :rtype: array of int
    """

    n_species=len(species)
    n_env=len(environments)
    D = np.zeros(n_species*n_env, dtype=float)
    for s in range(n_species):
        for e in range(n_env):
            if type(species[s].D) == dict :
                D[s*n_env+e] = species[s].D.get(environments[e], UnitValue(0, "µm2/s")).convert(units_system).value
            else :
                D[s*n_env+e] = species[s].D.convert(units_system).value
    return D

def simulate_3D(system, t_sample, time_step, engine_reference, seed, units_system, print_progress) :
    """
    perform a simulation in a 3D mesh grid.
    This function doesnt have a parameter validation routine, paramereters are expected to have been checked and processed before.
    Parameters are similar to those from the simulate function.

    :returns: simulation_data, t_sample
    :rtype: array of 2 UnitArrays
    """

    units_system = units_system.copy()
    units_system["quantity"] = "molecule"
    species=system.network.species
    reactions = []
    for r in system.network.reactions :
        rf, rr =r.split()
        reactions.append(rf)
        reactions.append(rr)
    environments = system.network.environments
    t_sample = t_sample.convert(units_system)
    engine = engine_reference.load()

    # initialize
    res = engine.initialize_3D(
            w           = system.space.w,
            h           = system.space.h,
            d           = system.space.d,
            n_species   = len(species),
            n_reactions = len(reactions),
            n_env       = len(environments),
            mesh_state  = system.state.convert(units_system).value,
            mesh_chstt  = system.chstt_map,
            mesh_env    = system.space.mesh_env,
            mesh_vol    = system.space.mesh_vol.convert(units_system).value,
            k           = build_reaction_rate_constant_array(reactions, units_system),
            sub         = build_substrate_stoechiometric_matrix(species, reactions),
            sto         = build_stoechiometric_difference_matrix(species, reactions),
            r_env       = build_reaction_environment_boolean_matrix(reactions, environments),
            D           = build_diff_coef_environment_matrix(species, environments, units_system),
            n_samples   = len(t_sample),
            t_sample    = t_sample.value,
            time_step   = time_step.convert(units_system).value,
            seed        = seed
            )

    if res == 1 :
        raise Exception("Invalid option argument : \""+engine.get_option()+"\".")

    if print_progress :
        print("0 %", end="")

    # iterate
    continue_simulation = True
    while continue_simulation :
        continue_simulation = engine.run(1000)
        if print_progress :
            print("\r" + str(engine.get_progress()) + " %", end="")

    # retriving the trajectories
    result = UnitArray(engine.get_output(), Units(units_system, quantity_units_dimensions()), check_value=False)

    # finalize
    engine.finalize()

    return result, t_sample
