import platform
import strengths
from strengths import rdengine

def _get_strengths_path():
        path = ""
        for i in strengths.__path__ :
            path += i
        return path

def _get_os_specific_engine_lib_name() :
    os = platform.system()
    if   os == "Windows" :
        return "engine_w.dll"
    elif os == "Linux" :
        return "engine_l.so"
    elif os == "Darwin" :
        return "engine_m.so"
    else :
        raise OSError("It seems that we havent planed any precompiled engine " +
                      "libaray for your operating system. You can try to " +
                      "build the engine dynamic library from sources, and then " +
                      "use it through a LibRDEngineRefrence object.")

def gillespie_engine():
    """
    Reference to an engine using a simple Euler method with a static time step.
    Diffusion is treated as a first order reaction according to Bernstein's method (Bernstein, 2005) [#Bernstein2005]_.
    
    :returns: engine reference.
    :rtype: LibRDEngineReference
    """
    # references :
    # .. [#Bernstein2005] Bernstein, D. (2005). Simulating mesoscopic reaction-diffusion systems using the Gillespie algorithm. Physical Review E, 71(4), Article 041103. https://doi.org/10.1103/PhysRevE.71.041103
    
    return rdengine.LibRDEngineReference(_get_strengths_path()+"/engines/strengths_engine/"+_get_os_specific_engine_lib_name(), "gillespie")

def tauleap_engine():  
    """
    Reference to an engine using the original Gillespie algorithm (Gillespie, 1977) [#Gillespie1977]_.
    Diffusion is treated as a first order reaction according to Bernstein's method (Bernstein, 2005) [#Bernstein2005]_.
    
    :returns: engine reference.
    :rtype: LibRDEngineReference
    """
    # references :
    # .. [#Bernstein2005] Bernstein, D. (2005). Simulating mesoscopic reaction-diffusion systems using the Gillespie algorithm. Physical Review E, 71(4), Article 041103. https://doi.org/10.1103/PhysRevE.71.041103
    # .. [#Gillespie1977] Gillespie, D. T. (1977). Exact stochastic simulation of coupled chemical reactions. The Journal of Physical Chemistry, 81(25), 2340-2361. https://doi.org/10.1021/j100540a008
    
    return rdengine.LibRDEngineReference(_get_strengths_path()+"/engines/strengths_engine/"+_get_os_specific_engine_lib_name(), "tauleap")

def euler_engine():
    """
    Reference to a LibRDEngine using the Gillespie tau leap method (Gillespie, 2001) [#Gillespie2001]_ with a static time step.
    Diffusion is treated as a first order reaction according to Bernstein's method (Bernstein, 2005) [#Bernstein2005]_.
    
    :returns: engine reference.
    :rtype: LibRDEngineReference
    """
    # references :
    # .. [#Bernstein2005] Bernstein, D. (2005). Simulating mesoscopic reaction-diffusion systems using the Gillespie algorithm. Physical Review E, 71(4), Article 041103. https://doi.org/10.1103/PhysRevE.71.041103
    # .. [#Gillespie2001] Gillespie, D. T. (2001). Approximate accelerated stochastic simulation of chemically reacting systems. The Journal of Chemical Physics, 115(4), 1716-1733. https://doi.org/10.1063/1.1378322
    
    return rdengine.LibRDEngineReference(_get_strengths_path()+"/engines/strengths_engine/"+_get_os_specific_engine_lib_name(), "euler")
