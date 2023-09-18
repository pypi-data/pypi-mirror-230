import strengths
import numpy as np
import ctypes
from strengths.typechecking import *

"""
Contains the RDEngineReferenceBase base class, as well as instances referring to the
simulation engines proposed by Strengths.
"""

class RDEngineBase :
    """
    base class for engine wrappers. they have an interface that
    is agnostic to strengths related concepts (classes, functions, etc.)
    and aims to unifiy engine interfaces.

    The typical flow when using a RDEngine is the following : 
    
    1) creating the engine object, with or without option (strengths.rdengine.RDEngine.__init__).
    2) (optionnal) setting the option. It can be done now it it had not been done at the object creation (strengths.rdengine.RDEngine.set_option).
    3) initializing the simulation (strengths.rdengine.RDEngine.initialize_3D).
    4) running the simulation until it is complete (strengths.rdengine.RDEngine.Run), along with the optionnal posibility to get the simulation progress (strengths.rdengine.RDEngine.get_progress).
    5) retriving the trajectory data (strengths.rdengine.RDEngine.get_output).
    6) finalizing the simulation (strengths.rdengine.RDEngine.finalize).
    
    :param option: engine option (default = "").
    :type option: str
        
    """

    def __init__(self, option = "") :
        """
        constructor.
        """
        
        self._option = option

    def get_option(self):
        """
        Returns the option currently associated with the engine.
        Should be called before initialize_3D.
        
        :rtype: str
        """
        
        return self._option

    def set_option(self, option):
        """
        Set the option to be associated with the engines.
        Should be called before initialize_3D.
        
        :param option: new option
        :type option: str
        """
        
        self._option = option

    def initialize_3D(self,
                      w,
                      h,
                      d,
                      n_species,
                      n_reactions,
                      n_env,
                      mesh_state,
                      mesh_chstt,
                      mesh_env,
                      mesh_vol,
                      k,
                      sub,
                      sto,
                      r_env,
                      D,
                      n_samples,
                      t_sample,
                      time_step,
                      seed,
                      option = None
                      ) :
        """
        initialize the reaction-diffusion simulation in a 3D mesh grid.
        
        :param w: mesh grid width.
            typically, w corresponds to MeshGrid.w.
        :type w: int
    
        :param h: mesh grid height.
            typically, h corresponds to MeshGrid.h.
        :type h: int
        
        :param d: mesh grid depth.
            typically, d corresponds to MeshGrid.d.
        :type d: int
        
        :param n_species: number of species in the reaction network.
            typically, n_species corresponds to RDNetwork.nspecies().
        :type n_species: int
    
        :param n_reactions: number of irreversible reactions network, excluding diffusion reactions.
            typically, n_reactions corresponds to 2*RDNetwork.nreactions(), since Reaction objects describe reversible reactions.
        :type n_reactions: int
    
        :param n_env: number of envirionments defined in the reaction network.
            typically, n_env corresponds to RDNetwork.nenvironments().
        :type n_env: int
        
        :param mesh_state: array describing the initial state of the reaction diffusion system, 
            which is the quantity of each species in each mesh of the system.
            typically, mesh_state corresponds to RDSystem.state.value, after units homogeneization.
        :type mesh_state: array

        :param mesh_chstt: array describing the distribution of chemostats inside the system.
            typically, mesh_chstt corresponds to RDSystem.chstt_map.
        :type mesh_chstt: array

        :param mesh_vol: volume of a single mesh.
            typically, mesh_vol corresponds to RDSystem.mesh_vol.value, after units homogeneization.
        :type mesh_vol: number

        :param k: array of the kinetic rates constants associated to each of the n_reactions irreversible reactions.
        :type k: array

        :param sub: array representing the linearized substrate stoechiometric matrix associating the n_reactions reactions to the n_species species.
            here is a example :
            let us say we have two species "A" (1) and "B" (2), and two irreversible reactions "2 A -> B" (1), "B -> 2 A" (2).
            the corresponding substrate stoechiometry matrix is :
        :type sub: array

        :param sto: array of the kinetic rates constants associated to each of the n_reactions irreversible reactions.
            here is a example :
            let us say we have two species "A" (1) and "B" (2), and two irreversible reactions "2 A -> B" (1), "B -> 2 A" (2).
            the corresponding substrate stoechiometry matrix is :
        :type sto: array

        :param renv: linearized boolean matrix telling if a given reaction can happen in a given environment.
        :type renv: array

        :param D: linearized matrix giving the diffusion coefficient of any species in any environmment.
        :type D: array
        
        :param n_samples: number of samples. (size of the t_sample array)
        :type n_samples: int
        
        :param t_sample: in-simulation timepoints at which the system state should be samped during the simulation.
        :type t_sample: array
        
        :param time_step: simulation time step, if used
        :type time_step: number
        
        :param seed: seed for the engine random number generator
        :type seed: int
        
        :param option: engine option to be used. if ignored or set to none, the engine attribute of the instance will be used instead.
        :type option: str or None
        
        :returns: 0 if the initialization went well, another value otherwise.
        :rtype: int
        """
        
        raise NotImplementedError("")

    def run(self, breathe_dt) :
        """
        Makes the engine keep iterating for until some ral-time time_limit or until the sulation is complete.
        Should be called after initialize_3D and before get_output and finalize.
        
        :param breathe_dt: maximal real-time duration for which the engine should keep running in ms.
        :type breathe_dt: int
        :returns: 0 if the simulation is complete, 1 otherwise.
        :rtype: int
        """
        
        raise NotImplementedError("")

    def get_progress(self) :
        """
        Returns the percentage of simulation progress.
        Should be called after initialize_3D and before finalize.
        
        :rtype: number
        """
        
        raise NotImplementedError("")

    def get_output(self) :
        """
        Returns the system trajectory data array.
        Should be called after initialize_3D and before finalize.

        :rtype: array
        """
        
        raise NotImplementedError("")

    def finalize(self) :
        """
        Finalize the engine use.
        Should be called last.
        """
        
        raise NotImplementedError("")

def _make_ctypes_array(a, t) :
    """
    make a ctype array of type t from the array a.
    """

    l = len(a)
    b = (t*l)()
    for i in range(l):
        b[i] = a[i]
    return b

class LibRDEngine(RDEngineBase) :
    """
    wrapper around engines implemented as dynamic libraries / DLLs.
    """

    def __init__(self, lib, option="") :
        self.lib = lib
        super(LibRDEngine, self).__init__(option)

    def initialize_3D(self,
                      w,
                      h,
                      d,
                      n_species,
                      n_reactions,
                      n_env,
                      mesh_state,
                      mesh_chstt,
                      mesh_env,
                      mesh_vol,
                      k,
                      sub,
                      sto,
                      r_env,
                      D,
                      n_samples,
                      t_sample,
                      time_step,
                      seed,
                      option = None
                      ) :

        if isnone(option) :
            option = self._option

        self._output_size = n_samples*n_species*w*h*d

        r = self.lib.Initialize3D(
                ctypes.c_int(w),
                ctypes.c_int(h),
                ctypes.c_int(d),
                ctypes.c_int(n_species),
                ctypes.c_int(n_reactions),
                ctypes.c_int(n_env),
                _make_ctypes_array(mesh_state, ctypes.c_double),
                _make_ctypes_array(mesh_chstt, ctypes.c_int),
                _make_ctypes_array(mesh_env,   ctypes.c_int),
                ctypes.c_double(mesh_vol),
                _make_ctypes_array(k,          ctypes.c_double),
                _make_ctypes_array(sub,        ctypes.c_int),
                _make_ctypes_array(sto,        ctypes.c_int),
                _make_ctypes_array(r_env,      ctypes.c_int),
                _make_ctypes_array(D,          ctypes.c_double),
                ctypes.c_int(n_samples),
                _make_ctypes_array(t_sample,   ctypes.c_double),
                ctypes.c_double(time_step),
                ctypes.c_int(seed),
                ctypes.c_char_p((option).encode())
                )

        return int(r)

    def run(self, breathe_dt) :
        r = self.lib.Run(breathe_dt)
        return int(r)

    def get_progress(self) :
        progress = self.lib.GetProgress()
        return float(progress)

    def get_output(self) :
        """
        :returns: system state trajectory data
        :rtype: array of number
        """
        r = (self._output_size*ctypes.c_double)()
        self.lib.GetOutput(r)
        output = np.zeros(self._output_size)
        for i in range(self._output_size) :
            output[i] = r[i]
        return output

    def finalize(self) :
        self.lib.Finalize()

class RDEngineReferenceBase :
    """
    Base class for engine references.
    """

    def load(self) :
        raise NotImplementedError("")

class LibRDEngineReference(RDEngineReferenceBase) :
    """
    Rreference to a LibEngineWrapper.
    """

    def __init__(self, path, option) :
        self._path = path
        self._option = option

    def load(self) :
        lib = ctypes.CDLL(self._path)
        lib.GetProgress.restype = ctypes.c_double
        engine = LibRDEngine(lib, self._option)
        return engine
