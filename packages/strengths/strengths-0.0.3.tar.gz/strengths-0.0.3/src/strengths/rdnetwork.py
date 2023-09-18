import numpy as np
import json
import strengths.value_processing as valproc
from strengths.units import *

"""
Module that contains the implementation of the ReactionNetwork and related classes, such as Species, Reactions, as well as related conversion and loading/saving functions.
"""

class Species :
    """
    A chemical species.

    :param label: unique label identifying the species in a reaction network
    :param type: str
    :param D: species diffusion coefficient (default 0).
    :type D: see D property
    :param density: species initial quantity (default 0).
    :type density: see density property
    :param chstt: species chemostate (default False).
    :type chstt: see chstt property
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitSystem or dict

    """
    def __init__(self, label, D = 0, density = 0, chstt = False, units_system = UnitsSystem()) :
        """
        constructor
        """

        self.units_system = units_system.copy()
        self._set_label(label)
        self.D = D
        self.density = density
        self.chstt = chstt

    @property
    def D(self):
        """
        Diffusion coefficient of the species (:py:class:`UnitValue` or :py:class:`dict` of :py:class:`UnitValue`).
        In term of unit dimensions, it have to be {"space" : 2, "time" : -1}.

        It can be defined by a number, a :py:class:`UnitValue`, a :py:class:`str` or environment wise by using a dict (of numbers, :py:class:`UnitValue` and :py:class:`str`).
        ie.

        .. code:: python

            rdnetwork.D = 0.5
            rdnetwork.D = "0.5 µm2.s-1"
            rdnetwork.D = UnitValue(0.5, "µm2/s")
            rdnetwork.D = {"env_1" : "0.5 µm2.s-1",
                           "env_2" :  5}
        """

        return self._D

    @D.setter
    def D(self, D):
        self._D = valproc.process_unitvar_input(
            D,
            self.units_system,
            {"space" : 2, "time" : -1, "quantity" : 0},
            accepts_singlevalue = True,
            accepts_dict = True,
            accepts_array = False)

    @property
    def density(self):
        """
        default density of the species in systems (:py:class:`UnitValue` or :py:class:`dict` of :py:class:`UnitValue`).
        In term of unit dimensions, it have to be a density.
        It can be define by a number, a :py:class:`UnitValue`, a :py:class:`str` or environment wise by using a dict (of numbers, :py:class:`UnitValue` and :py:class:`str`).
        ie.

        .. code:: python

            rdnetwork.D = 5
            rdnetwork.D = "0.5 µM"
            rdnetwork.D = UnitValue(0.5, "µM")
            rdnetwork.D = {"env_1" : "0.5 µM",
                           "env_2" : "5 nM"}

        """

        return self._density

    @density.setter
    def density(self, density):
        self._density = valproc.process_unitvar_input(
            density,
            self.units_system,
            density_units_dimensions(),
            accepts_singlevalue = True,
            accepts_dict = True,
            accepts_array = False)

    @property
    def chstt(self):
        """
        tells if the quantity of this species should be by default considered constant (:py:class:`bool` or :py:class:`dict` of :py:class:`bool`).
        it can be a boolean (True is the species is chemostated, False otherwise),
        or a dictionary associating a boolean to some environment.
        ie.

        .. code:: python

            { "membrane" : True,
              "cytoplasm" : False }

        """

        return self._chstt

    @chstt.setter
    def chstt(self, chstt):
        if isdict(chstt) :
            self._chstt = chstt
        elif isnumber(chstt) :
            self._chstt = bool(chstt)
        else :
            raise TypeError("species chstt must be a boolean (or a type that can be catsed as such) or dict")

    @property
    def label(self):
        """
        string identifyling the species inside a reaction network (:py:class:`str`).
        can be thought as the name of the species.
        a species must have one.
        """

        return self._label

    def _set_label(self, label):
        if not (isnone(label) or isstr(label)) :
            raise TypeError("label must be a string.")
        self._label = label

    @property
    def units_system(self):
        """
        default units system used when value that require units are given without (:py:class:`UnitsSystem`).
        can be defined from a :py:class:`UnitsSystem` or a :py:class:`dict`.
        ie.

        .. code:: python

            species.units_system = UnitsSystem(space="µm", time="s", quantity="molecule")
            species.units_system = {"space"="µm", "time"="s", "quantity"="molecule"}

        """

        return self._units_system

    @units_system.setter
    def units_system(self, units_system):
        if isdict(units_system) :
            self._units_system = unitssystem_from_dict(units_system)
        elif type(units_system) == UnitsSystem :
            self._units_system = units_system.copy()
        else :
            raise TypeError("units_system must be a dict or an instance of UnitsSystem.")

    def copy(self) :
        """
        returns a deepcopy of the instance.

        .. code:: python

            instance.copy()

            # is equivalent to
            # import copy

            copy.deepcopy(instance)

        """

        return cpy.deepcopy(self)

class Reaction :
    """
    A reversible chemical transformation that converts some species into others with respect to a forward and a reverse kinetic rate constants.

    :param stoechiometry: stoechiometry of the reaction.
        can be a string the "substrate -> product" (ie. "A + 2 B -> C")
        or an array of two dictonaries, the first representing the subtrates, and the second the products.
        each dictionary must then contain species labels as keys and numbres as values. (ie. [{"A":1, "B":2}, {"C":1}]).
    :param kf: forward reaction rate constant
    :param kr: reverse reaction rate constant (default 0)
    :param label: unique identifier for the reaction in a reaction network. (default None)
    :type label: str or None
    :param environments: list of environment in which the reaction can occur (default None).
        if None, the reaction can occur everywhere.
    :type environments: None or list[str].
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitSystem or dict

    """

    def __init__ (self, stoechiometry, kf, kr=0, label = None, environments = None, units_system = UnitsSystem()) :
        """
        constructor
        """

        self.units_system = units_system.copy()

        if type(stoechiometry) == str :
            self._fromstring(stoechiometry)
        else :
            self._substrates = {}
            self._products = {}
            for k in list(stoechiometry[0]) :
                self._substrates[k] = int(stoechiometry[0][k])
            for k in list(stoechiometry[1]) :
                self._products[k] = int(stoechiometry[1][k])

        self._set_label(label)
        self.environments = environments
        self.set_k(kf, kr)

    @property
    def kf(self) :
        """
        Forward reaction rate constant (:py:class:`UnitsSystem`).
        can be set by a number, a :py:class:`str` or a :py:class:`UnitValue`.
        ie.

        .. code:: python

            reaction.kf = 1
            reaction.kf = UnitValue(1, "µM-1.s-1")
            reaction.kf = "1 µM-1.s-1"
        """

        return self._kf

    @kf.setter
    def kf(self, kf) :
        self._kf = valproc.process_unitvar_input(
            kf,
            self.units_system,
            self.kf_units_dimensions(),
            accepts_singlevalue = True,
            accepts_dict = False,
            accepts_array = False)
    @property
    def kr(self) :
        """
        Reverse reaction rate constant (:py:class:`UnitsSystem`).
        can be set by a number, a :py:class:`str` or a :py:class:`UnitValue`.
        see k+ example above.
        """

        return self._kr

    @kr.setter
    def kr(self, kr) :
        self._kr = valproc.process_unitvar_input(
            kr,
            self.units_system,
            self.kr_units_dimensions(),
            accepts_singlevalue = True,
            accepts_dict = False,
            accepts_array = False)

    @property
    def environments(self) :
        """
        list of environments labels in which the reaction can happen. if None, the reaction can happen in any environment.
        """

        return self._environments

    @environments.setter
    def environments(self, environments) :
        if not (isarray(environments) or isnone(environments)):
            raise TypeError("reaction environments must be an array.")

        if isnone(environments) :
            self._environments = None
        else :
            self._environments = environments.copy()

    @property
    def label(self):
        """
        string used to identiify the reation inside a rdNetwork.
        it is optional, and is None by default.
        """

        return self._label

    def _set_label(self, label):
        if not (isnone(label) or isstr(label)) :
            raise TypeError("label must be a string.")
        self._label = label

    @property
    def units_system(self):
        """
        default units system used when value that require units are given without (:py:class:`UnitsSystem`).
        can be defined from a :py:class:`UnitsSystem` or a :py:class:`dict`.
        ie.

        .. code:: python

            reaction.units_system = UnitsSystem(space="µm", time="s", quantity="molecule")
            reaction.units_system = {"space"="µm", "time"="s", "quantity"="molecule"}
        """

        return self._units_system

    @units_system.setter
    def units_system(self, units_system):
        if isdict(units_system) :
            self._units_system = unitssystem_from_dict(units_system)
        elif type(units_system) == UnitsSystem :
            self._units_system = units_system.copy()
        else :
            raise TypeError("units_system must be a dict or an instance of UnitsSystem.")

    def set_k(self, kf, kr) :
        """
        Sets the reaction's forward and reverse kinetics rate constants, respectively.

        :param kf: forward reaction rate.
        :type kf: number or UnitValue
        :param kr: reverse reaction rate.
        :type kr: number or UnitValue
        """

        self.kf = kf
        self.kr = kr

    def ssto(self, species_labels) :
        """
        Returns the substrates stoechiometry array corresponding to **species_labels**.

        :param species_labels: list of species labels. For a given RDNetwork rdn, it must be ordered as in rdn.species_labels.
        :type species_labels: array of str
        :returns: substrate stoechiometry coefficient for each species.
        :rtype: array of int
        """

        return [int(self._substrates.get(s, 0)) for s in species_labels]

    def psto(self, species_labels) :
        """
        Returns the products stoechiometry array corresponding to **species_labels**.

        :param species_labels: list of species labels. For a given RDNetwork rdn, it must be ordered as in rdn.species_labels.
        :type species_labels: array of str
        :returns: product stoechiometry coefficient for each species.
        :rtype: array of int
        """

        return [int(self._products.get(s, 0)) for s in species_labels]

    def dsto(self, species_labels) :
        """
        Returns the transformation change (products-substrates) stoechiometry array corresponding to **species_labels**.

        :param species_labels: list of species labels. For a given RDNetwork rdn, it must be ordered as in rdn.species_labels.
        :type species_labels: array of str
        :returns: product-substrate stoechiometry coefficient for each species.
        :rtype: array of int
        """

        return [int(self._products.get(s, 0))-int(self._substrates.get(s, 0)) for s in species_labels]

    def get_substrate_stoechiometry(self, species_label) :
        """
        returns the substrate stoechimetry of a given species.
        :param species_label: label of the species
        :type species_label: str
        :returns: substrate side stoechiometric coefficient for the given species
        :rtype: int
        """

        s = self._substrates.get(species_label, 0)
        return s

    def get_product_stoechiometry(self, species_label) :
        """
        returns the product stoechimetry of a given species.
        :param species_label: label of the species
        :type species_label: str
        :returns: product side stoechiometric coefficient for the given species
        :rtype: int
        """

        s = self._products.get(species_label, 0)
        return s

    def _fromstring(self, string) :
        """
        Sets the stoechimetry of the reaction from a string representing its stoechimetric equation.
        """

        def parse_side(side) :
            d = {}
            tokens = side.split("+")
            if not(len(tokens)==1 and tokens[0].strip() == "") :
                for token in tokens :
                    token = token.strip().split()
                    coef, label = 1, ""
                    if len(token) == 1 :
                        label = token[0].strip()
                    elif len(token) == 2 :
                        coef = int(token[0].strip())
                        label = token[1].strip()
                    else :
                        raise Exception("invalid stoechiometry equation. missing '+'?")

                    if d.get(label, None) == None :
                        d[label] = coef
                    else:
                        d[label] += coef
            return d

        sides = string.split('->')
        if len(sides) != 2 :
            raise Exception("stoechimetry equation string must have exactly one '->'.")

        self._substrates = parse_side(sides[0])
        self._products   = parse_side(sides[1])

    def to_string(self):
        """
        Returns a string representing the reaction's stoechimetric equation (:py:class:`str`).
        """

        def encode_side(d) :
            string = ""
            first = True
            for s in list(d) :
                if d[s] != 0 :
                    if not first :
                        string += "+ "
                    first = False
                    if d[s] != 1 :
                        string += str(d[s]) + " "
                    string += s + " "
            return string
        return encode_side(self._substrates) + "-> "+encode_side(self._products)

    def kf_units_dimensions(self):
        """
        Returns the units dimensions of the forward reaction rate (:py:class:`UnitsDimensions`).
        """

        count = 0
        for k in list(self._substrates) :
            count += self._substrates[k]
        return UnitsDimensions(space = -3 + 3*count ,time = -1 ,quantity = 1-count)

    def kr_units_dimensions(self):
        """
        Returns the units dimensions of the reverse reaction rate (:py:class:`UnitsDimensions`).
        """

        count = 0
        for k in list(self._products) :
            count += self._products[k]
        return UnitsDimensions(space = -3 + 3*count ,time = -1 ,quantity = 1-count)

    def split(self) :
        """
        split the reaction into a pair of opposed irreversible reactions (with kr=0).
        returned reactions have the same properties than the splitted reaction,
        except for their label, which are NULL.

        example :

        .. code::

            r = Reaction("A + B -> C",
                     kf=2,
                     kr=1,
                     label="association",
                     environments=["env1"],
                     units_system=UnitsSystem(space="m",
                                              time="min",
                                              quantity="mol")
                     )

            r_forward, r_reverse = r.split()

            # is equivalent to

            r_forward = Reaction("A + B -> C",
                     kf=2,
                     kr=0,
                     label=None,
                     environments=["env1"],
                     units_system=UnitsSystem(space="m",
                                              time="min",
                                              quantity="mol")
                     )

            r_reverse = Reaction("C -> A + B",
                     kf=1,
                     kr=0,
                     label=None,
                     environments=["env1"],
                     units_system=UnitsSystem(space="m",
                                              time="min",
                                              quantity="mol")
                     )

        :returns: a list of two Reaction objects. The first corrspond to the forward irreversible reaction,
            the second, to the reverse irreversible reaction.
        :rtype: list of Reaction
        """

        fwd = Reaction(
            stoechiometry = [self._substrates, self._products],
            kf = self.kf,
            kr = 0,
            label=None,
            environments = self.environments,
            units_system = self.units_system
            )
        rev = Reaction(
            stoechiometry = [self._products, self._substrates],
            kf = self.kr,
            kr = 0,
            label=None,
            environments = self.environments,
            units_system = self.units_system
            )
        return fwd, rev

    def equilibrium_constant(self) : 
        """
        Returns the reaction equilibrium constant K = kf/kr.
        
        :rtype: UnitValue
        """
        
        return self.kf/self.kr
    
    def copy(self) :
        """
        returns a deepcopy of the instance.

        .. code:: python

            instance.copy()

            # is equivalent to
            # import copy

            copy.deepcopy(instance)

        """

        return cpy.deepcopy(self)

class RDNetwork :
    """
    A network of chemical transformations (:py:class:`Reaction`) and chemical species (:py:class:`Species`).

    :param species: list of species
    :type species: array of Species
    :param reactions: list of reactions
    :type reactions: array of Reactions
    :param environments: list of environment labels (default [""])
    :type environments: array of str
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitSystem or dict

    """

    def __init__ (self, species, reactions, environments = [""], units_system = UnitsSystem()) :
        """
        constructor
        """

        self.units_system = units_system.copy()
        self.reactions = reactions
        self.species = species
        self.environments = environments

    @property
    def reactions(self) :
        """
        Reactions of the network (tuple of :py:class:`Reaction`).
        """

        return self._reactions

    @reactions.setter
    def reactions(self, reactions) :
        if isarray(reactions) :
            for r in reactions :
                if type(r) != Reaction :
                    raise TypeError("reactions must be an array of Reactions")
        else :
            raise TypeError("reactions must be an array")

        self._reactions = tuple(reactions)

    @property
    def species(self) :
        """
        Species of the network (tuple of :py:class:`Species`).
        """

        return self._species

    @species.setter
    def species(self, species) :
        if isarray(species) :
            for s in species :
                if type(s) != Species :
                    raise TypeError("species must be an array of Species")
        else :
            raise TypeError("species must be an array")

        self._species = tuple(species)

    @property
    def environments(self) :
        """
        Labels of the different environments of the network (array of :py:class:`str`).
        it must be a non-empty list of string.
        ie.

        .. code:: python

            environments = []              # wrong : the array is empty
            environments = [1]             # wrong : the 1 is not a string
            environments = ["a", "b", "c"] # ok

        means the systems have 3 environments labelled "a", "b" and "c".
        The order of the labels matters, as here, "a", "b" and "c" have mesh environment indices
        0, 1 and 2, and those indices are the one used in RDSystem.mesh_env.

        """

        return self._environments

    @environments.setter
    def environments(self, environments) :
        if isarray(environments) :
            if len(environments)==0 :
                raise ValueError("environments array must not be empty.")
            for e in environments :
                if type(e) != str :
                    raise TypeError("environments must be an array of strings only")
        else :
            raise TypeError("environments must be an array (of strings).")
        self._environments = environments.copy()

    @property
    def units_system(self):
        """
        default units system used when value that require units are given without (:py:class:`UnitsSystem`).
        can be defined from a :py:class:`UnitsSystem` or a :py:class:`dict`.
        ie.

        .. code:: python

            rdnetwork.units_system = UnitsSystem(space="µm", time="s", quantity="molecule")
            rdnetwork.units_system = {"space"="µm", "time"="s", "quantity"="molecule"}
        """

        return self._units_system

    @units_system.setter
    def units_system(self, units_system):

        if isdict(units_system) :
            self._units_system = unitssystem_from_dict(units_system)
        elif type(units_system) == UnitsSystem :
            self._units_system = units_system.copy()
        else :
            raise TypeError("units_system must be a dict or an instance of UnitsSystem.")

    def nreactions(self) :
        """
        Returns the number of reactions in the network.
        """

        return len(self.reactions)

    def nspecies(self) :
        """
        Returns the number of species in the network.
        """

        return len(self.species)

    def nenvironments(self) :
        """
        Returns the number of environments in the network.
        """

        return len(self.environments)

    def species_labels(self) :
        """
        Returns the array of the labels of the network's species.
        """

        return [s.label for s in self.species]

    def get_species(self, label) :
        """
        Returns the first species with the given label, or none otherwise  (:py:func:`Species` or :py:const:`None`).
        """

        for s in self.species :
            if s.label == label :
                return s
        return None

    def get_reaction(self, label) :
        """
        Returns the first reaction with the given label, or none otherwise (:py:func:`Reaction` or :py:const:`None`).
        """

        for r in self.reactions :
            if r.label == label :
                return r
        return None

    def get_species_index(self, species) :
        """
        Returns the species list index associated with the given input.
        if species is a string or a Species, the index of the first species with a matching label is returned.
        if species is a number, int(species) is returned if 0<=species<nspecies.
        in case no index can be found, None is returned.

        :param species: species from which we want the index.
        :type species: number, str or Species
        :returns: index of the species
        :rtype: int
        """

        if isnumber(species) :
            index = int(species)
            if index>=0 and index<self.nspecies() :
                return index
            else :
                return None
        elif isstr(species) :
            for i in range(self.nspecies()) :
                if self.species[i].label == species :
                    return i
            return None
        elif type(species) == Species :
            for i in range(self.nspecies()) :
                if self.species[i].label == species.label :
                    return i
            return None
        else :
            raise TypeError("species must be a Species, a number or a string.")

    def get_reaction_index(self, reaction) :
        """
        Returns the Reaction list index associated with the given input.
        if reaction is a string or a Reaction, the index of the first reaction with a matching label is returned.
        if reaction is a number, int(reaction) is returned if 0<=reaction<nreactions.
        in case no index can be found, None is returned.

        :param reaction: reaction from which we want the index.
        :type reaction: number, str or Reaction
        :returns: index of the reaction
        :rtype: int
        """

        if isnumber(reaction) :
            index = int(reaction)
            if index>=0 and index<self.nreactions() :
                return index
            else :
                return None
        elif isstr(reaction) :
            for i in range(self.nreactions()) :
                if self.reactions[i].label == reaction :
                    return i
            return None
        elif type(reaction) == Reaction :
            for i in range(self.nreactions()) :
                if self.reactions[i].label == reaction.label :
                    return i
            return None
        else :
            raise TypeError("reaction must be a Reaction, a number or a string.")

    def copy(self) :
        """
        returns a deepcopy of the instance.

        .. code:: python

            instance.copy()

            # is equivalent to
            # import copy

            copy.deepcopy(instance)

        """

        return cpy.deepcopy(self)

def species_from_dict(d, units_system = UnitsSystem()):
    """
    Returns a Species created acoording to the dictionnary d.

    :param d: dictionary representing the species
    :type d: dict
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitsSystem
    :returns: species created from d.
    :rtype: Species
    """

    d = valproc.process_input_dict_keys(d, [
                ["label", "l"],
                ["D", "diff_coef", "diffusion_coefficient", "diff coef", "diffusion coefficient"],
                ["density", "concentration", "dens", "conc", "C"],
                ["chstt", "chemostate"],
                ["units", "units_system", "units system", "u"]
            ]
        )

    return Species(label=d["label"],
                   D=d.get("D", 0),
                   density=d.get("density", 0),
                   chstt=d.get("chstt", False),
                   units_system=d.get("units", units_system))

def species_to_dict(s):
    """
    Returns a dict represnting the Species s.

    :param s: species to be represented as a dict
    :type s: Species
    :returns: dict created from s.
    :rtype: dict
    """
    d = {"label" : s.label,
         "D" : valproc.format_unitvar_for_save(s.D, s.units_system),
         "density" : valproc.format_unitvar_for_save(s.density, s.units_system),
         "chstt" : s.chstt,
         "units" : unitssystem_to_dict(s.units_system)

        }
    return d

def reaction_from_dict(d, units_system = UnitsSystem()):
    """
    Returns a Reaction created acoording to the dictionnary d.

    :param d: dictionary representing the reaction
    :type d: dict
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitsSystem
    :returns: reaction created from d.
    :rtype: Reaction
    """

    d = valproc.process_input_dict_keys(d, [
                ["stoechiometry", "sto", "equation", "eq"],
                ["label", "l"],
                ["k+", "kf", "k_+", "k_f"],
                ["k-", "kr", "k_-", "k_r"],
                ["environments", "env"],
                ["units", "units_system", "units system", "u"]
            ]
        )

    return Reaction(stoechiometry=d["stoechiometry"],
                    kf=d.get("k+", 0),
                    kr=d.get("k-", 0),
                    label=d.get("label", None),
                    environments=d.get("environments", None),
                    units_system=d.get("units", units_system))

def reaction_to_dict(r):
    """
    Returns a dict representing the Reaction r.

    :param r: reaction to be represented as a dict
    :type r: Reaction
    :returns: dict created from r.
    :rtype: dict
    """
    d = {"label" : r.label,
         "stoechiometry" : r.to_string(),
         "k+" : valproc.format_unitvar_for_save(r.kf, r.units_system),
         "k-" : valproc.format_unitvar_for_save(r.kr, r.units_system),
         "environements" : r.environments,
         "units" : unitssystem_to_dict(r.units_system)
        }
    return d

def rdnetwork_from_dict(d, units_system = UnitsSystem()):
    """
    Returns a RDNetwork created acoording to the dictionnary d.

    :param d: dictionary representing the reaction network
    :type d: dict
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitsSystem
    :returns: reaction network created from d.
    :rtype: RDNetwork
    """

    d = valproc.process_input_dict_keys(d, [
                ["species"],
                ["reactions"],
                ["environments", "env"],
                ["units", "units_system", "units system", "u"]
            ]
        )

    environments = d.get("environments", [""])
    units = d.get("units", units_system)
    species=[]
    reactions=[]

    for s in d["species"] :
        species.append(
            species_from_dict(s, units))

    for r in d["reactions"] :
        reactions.append(
            reaction_from_dict(r, units))

    rn = RDNetwork(species=species, 
                   reactions=reactions, 
                   environments=environments, 
                   units_system=units)
    
    return rn

def rdnetwork_to_dict(rdn):
    """
    Returns a dictionnary describing the reaction network.

    :param rdn: reaction network to be converted
    :type rdn: ReactionNetwork
    :returns: dictionary representing rdn.
    """

    d = {"units" : unitssystem_to_dict(rdn.units_system),
         "species"   : [species_to_dict(s) for s in rdn.species],
         "reactions" : [reaction_to_dict(r) for r in rdn.reactions],
         "environments" : rdn.environments
         }
    return d

def load_rdnetwork(path, units_system = UnitsSystem()):
    """
    Returns a ReactionNetwork created acoording to the dictionnary d loaded from the JSON file at the given path.

    :param path: relative or absolute path to a json file.
    :type path: str
    :param units_system: default units system (default UnitsSystem())
    :type units_system: UnitsSystem
    :returns: reaction network built according to the JSON file.
    """

    f = open(path, "r", encoding="utf-8")
    d = json.load(f)
    return rdnetwork_from_dict(d, units_system)

def save_rdnetwork(rdn, path):
    """
    Saves the dictionnary desctiption of the reaction network **rdn** as a JSON file at the given **path**.

    :param rdn: reaction network to be saved as a JSON file.
    :type rdn: ReactionNetwork
    :param path: JSON save file relative or absolute path.
        a JSON is created at this location, or replaced if it already exists
    :type path: str
    :returns: None
    """

    d = rdnetwork_to_dict(rdn)
    f = open(path, "w", encoding="utf-8")
    json.dump(d, f, indent = 4)
    f.close()
