from strengths.units import *
from strengths.typechecking import *
import copy

"""
processing of variables.
"""

def is_unitarray_dict(d) :
    """
    returns true id d is a dict representing akin to represent a unitarray (a dict that possesses a "units"
    or a "value" key).
    """
    
    if not isdict(d) :
        return False
    
    return ((d.get("units", None) != None) or (d.get("value", None) != None))
    
    
def process_unitvar_input (
        v, 
        units_system, 
        units_dimensions,
        accepts_singlevalue,
        accepts_dict,
        accepts_array
        ) :
    """
    processing of function arguments expecting UnitValues, UnitArrays of dict of UnitValues/UnitArrays.

    Return a value equivalent to v, where numbers/arrays have been replaced by UnitValue/UnitArrays.
    Preexisting UnitValue/UnitArrays are checked to have the same dimensions as the one specified
    in the arguments, a ValueError is raised otherwise.
    """

    v = copy.deepcopy(v)
    
    if is_unitarray_dict(v) : 
        v = unitarray_from_dict(v)
    elif isdict(v) :
        for k in list(v) :
            if is_unitarray_dict(v[k]) :
                v[k] = unitarray_from_dict(v[k])
    
    v_out = copy.deepcopy(v)

    # if v is a dict, all value numbers are replaced by UnitValues
    if type(v) == dict :
       
        # raise an error if dicts are not accepted for the property
        if not accepts_dict : 
            raise ValueError("this property does not accepts dict as input value")

        for k in list(v) :
            if isnumber(v[k]) : 
                if not accepts_singlevalue : 
                    raise ValueError("this property does not accepts single values as input")
                    
                v_out[k] = UnitValue(v[k], Units(units_system, units_dimensions))
            elif type(v[k]) == UnitValue  or type(v[k]) == str :
                if not accepts_singlevalue : 
                    raise ValueError("this property does not accepts single values as input")
                    
                if type(v[k]) == str :
                    v_out[k] = parse_unitvalue(v[k])
                
                if v_out[k].units.dim != units_dimensions : 
                    raise ValueError("wrong dimensions.")
            elif isarray(v[k]) :
                if not accepts_array : 
                    raise ValueError("this property does not accepts arrays as input values")
        
                v_out[k] = UnitArray(v[k], Units(units_system, units_dimensions))
            elif type(v[k]) == UnitArray :
                if not accepts_array : 
                    raise ValueError("this property does not accepts arrays as input values")
        
                if v[k].units.dim != units_dimensions : 
                    raise ValueError("wrong dimensions.")
            else :
                raise TypeError("unexpected property dict value type.")
    
    # if v is a number, it is converted to a UnitValue
    elif isnumber(v) :
        if not accepts_singlevalue : 
            raise ValueError("this property does not accepts single values as input")
        
        v_out = UnitValue(v, Units(units_system, units_dimensions))

    # if v is a siring, it is parsed into a UnitValue.
    # if v is a UnitValue, or a string, the UnitValue dimensions is checked.
    elif type(v) == UnitValue  or type(v) == str :
        if not accepts_singlevalue : 
            raise ValueError("this property does not accepts single values as input")
            
        if type(v) == str :
            v_out = parse_unitvalue(v)
        if v_out.units.dim != units_dimensions : 
            raise ValueError("wrong dimensions : expected "+str(units_dimensions)+", got "+str(v_out.units.dim)+".")
    
    # if v is an array, it is converted to a UnitArray
    elif isarray(v) :
        if not accepts_array : 
            raise ValueError("this property does not accepts arrays as input value")

        v_out = UnitArray(v, Units(units_system, units_dimensions))
    
    # if v is a UnitArray, it its unit dimensions are chenched
    elif type(v) == UnitArray :
        if not accepts_array : 
            raise ValueError("this property does not accepts arrays as input value")

        if v.units.dim != units_dimensions : 
            raise ValueError("wrong dimensions.")
    
    # if none of the conditions above is met, a ValueError is raised.
    else :
        raise TypeError("unexpected property type. must be dict, number or UnitValue.")

    return v_out


def format_unitvar_for_save(v, units_system) :
    """
    returns str(v) if v's units system differs from us, the default units system, v.value otherwise.'
    """
    
    if type(v) == UnitValue : 
        if v.units.sys == units_system : 
            return v.value
        else :
            return str(v)
    elif type(v) == UnitArray : 
        if v.units.sys == units_system : 
            return v.value
        else :
            return unitarray_to_dict(v)
    elif type(v) == dict : 
        d = {}
        for k in list(v) :

            if type(v[k]) == UnitValue : 
                if v[k].units.sys == units_system : 
                    d[k] = v[k].value
                else :
                    d[k] = str(v[k])
            elif type(v[k]) == UnitArray : 
                if v[k].units.sys == units_system : 
                    d[k] = v[k].value
                else :
                    d[k] = unitarray_to_dict(v[k])            
                    
def process_input_dict_keys(d, synonyms, policy="error") :
    """
    process a dict given in input for functions such as thing_from_dict.
    
    :param d: dict to be processed
    :type d: dict
    :param synonyms: different key strings expected as well as their synonyms
        it must be a list of striung key synonyms list. Each key with one synonym in the list will be replaced by the 
        first key in the synonym list. synonyms, should not contain any duplicated key.
        ie.
            
        synonyms = [
        ["chemostates", chstt],
        ["mesh_volume", mesh_vol, mesh_v], 
        ...]
        
    :type synonyms: array[array[str]]
    :param policy: indicates how to manage unexpected or duplicated keys.
        expects :
            
        * "silent" : issues are ignored
        * "warning" : issues are presented through a console print
        * "error" : issues raise a ValueError exception
        
    :type policy: str
    :returns: processed dict with synonyms replaced.
    :rtype: dict
    """
    
    #first step : search for unexpected keys
    for k in list(d) : 
        key_found = False
        for s in synonyms : 
            if k in s : 
                key_found = True
                break
        if not key_found : 
            if policy == "error" :
                raise ValueError("unexcpected key \"" + k + "\" in input dictionary.")
            elif policy == "warning" :
                print("warning : unexcpected key \"" + k + "\" in input dictionary.")

    #second step : search for duplicated synonyms
    for s in synonyms : 
        synonyms_found = []
        for k in list(d) : 
            if k in s :
                synonyms_found.append(k)
        if len(synonyms_found)>1 : 
            if policy == "error" :
                raise ValueError("dictionnary key " + synonyms_found + " in input dictionary are synonyms.")
            elif policy == "warning" :
                print("warning : dictionnary key " + synonyms_found + " in input dictionary are synonyms.")
    
    #third step : replace synonyms
    for s in synonyms : 
        for k in list(d) : 
            if k in s :
                d[s[0]] = d[k]
    
    return d