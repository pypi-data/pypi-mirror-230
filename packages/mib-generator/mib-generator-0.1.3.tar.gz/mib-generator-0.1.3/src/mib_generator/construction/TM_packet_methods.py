"""Methods for creation of telemetry MIB tables and internal representation of TM packets in general.

This module holds methods that help with formatting of parsed data into monitoring packet characteristics. They are usually
concerned with value evaluation, bite counting, type identification etc. I.e. mostly kind of housekeeping jobs.
"""
from copy import copy

import mib_generator.data.longdata as longdata
import mib_generator.data.warn as warn
import mib_generator.parsing.load as load


def apidnum(name):
    """Find the value of apid from evaluation of references, etc.

    This method is probably unnecessarily complicated because I tried to follow a logic of C here, which seemed to have a
    missing link anyways. But what it does is simply looking up the value of apid based on its name. This value is stored
    in an array in the ``.c`` telemetry file and hence isn't included in the standard :obj:`mib_generator.parsing.load.enumerations` and
    hence has to be evaluated this more complicated way.

    Args:
        name (str): Name of the apid reference.

    Returns:
        int: Value of the apid reference.
    """
    num = load.enumerations[name]
    lis = next((x for x in load.TmC.structures if x.name == "apidNum"), None)
    link = {}
    for i in lis.elements:
        link[str(load.enumerations[i.position[1:-1]])] = int(i.value)
    return link[str(num)]


def evalu(string):
    """Evaluate the given expression using all known substitutions, macros, etc.

    This methods tries to evaluate the passed expression using various methods. First it tries a simple integer conversion,
    then it tries to evaluate it using the dictionary :obj:`mib_generator.parsing.load.enumerations` which stores all the possible substitutions
    found across the code. Then even if this doesn't work (e.g. the string contains algebraic expressions), tries to use Python's
    ``eval()`` function. If even this fails, it evaluates the expression as ``-1``.

    Args:
        string (str): A string which is to be evaluated.

    Returns:
        int: The evaluated value or ``-1`` if the evaluation failed.
    """
    try:
        x = int(string)
    except:
        if string in load.enumerations.keys():
            x = load.enumerations[string]
        else:
            try:
                x = eval(string, load.enumerations)
            except:
                x = -1
                warn.raises("WCM1", string)
    return x


def getptcpcf(entry, size):
    """Get ptc and pfc values from the size and nature of the given entry.

    From data type (in C) of the entry and information in its comments, tries to deduce what SCOS data type given by the ptc|pcf combination it
    should be assigned. Uses data from :obj:`mib_generator.data.longdata.time_pfc` and
    :obj:`mib_generator.data.longdata.uint_pfc`.

    Args:
        entry (parsing.par_header.misc_r): The entry who's value is to be evaluated.
        size (int): Bite-size of the entry.

    Returns:
        tuple: A tuple consisting of:

            * *int* - Value of ptc of the parameter.
            * *int* - Value of pfc of the parameter.
    """
    try:
        typ = entry.comment[-1].entries["type"]
    except:
        typ = "-1"
    if typ.startswith("CUCTIME"):
        ptc = 9
        pfc = longdata.time_pfc.index([int(typ[7]), int(typ[9])])
    elif entry.array != "-1":
        ptc = 7
        pfc = int(size / 8)
    elif entry.type.startswith("uint"):
        ptc = 3
        pfc = longdata.uint_pfc.index(size)
    elif entry.type == "enum":
        ptc = 2
        pfc = size
    else:
        ptc = 3
        pfc = 16
    return ptc, pfc


def categfromptc(ptc):
    """Get category from ptc value of the entry.

    Extracts the value of category entry in pcf table from the parameter's ptc type.

    This is automatically changed later if the parameter is subject to textual calibration.

    Args:
        ptc (int) - A ptc value of the parameter.

    Returns:
        str: The letter identifying the category.
    """
    if ptc in {2, 3, 6, 7, 9, 10}:
        categ = "N"
    elif ptc == 8:
        categ = "T"
    else:
        categ = "S"
    return categ


def header_search(typ):
    """Search for corresponding header structures of the packet based on information in the comments.

    Given the name of the packet as it appears in the TM ``.c`` file, this method searches among structures
    in :obj:`mib_generator.parsing.load.TmH` (the TM ``.h`` file) for a corresponding packet/packets description (list of parameters, etc).
    More packet definitions can correspond to a single type (they then differ in additional packet identifiers) and hence
    more than one such structures can be found sometimes.

    Args:
        typ (str): The "type" entry of the packet definition in the ``.c`` TM file.

    Returns:
        list: A list of structures which are packet descriptions for the given packet "type".
    """
    hstruct = []
    for i in load.TmH.structures:
        if i.type == "struct" and i.comment:
            uni = {}
            for l in i.comment:
                uni.update(l.entries)
            if "pack_type" in uni.keys() and uni["pack_type"] == typ:
                hstruct.append(i)
    # legacy approach
    # if typ in load.enumerations.keys() and not hstruct:
    #    hstruct.append(load.enumerations[typ])
    if not hstruct:
        warn.raises("WCM2", typ)
    return hstruct


def h_analysis(h_struct):
    """Make a list of all individual (all structs unpacked) entries in the packet.

    This method goes iteratively through all entries/packet parameters inside the given structure. If it finds a normal entry,
    it adds it to the list, if it finds a ``struct`` or reference to one, it expands it by recursively calling itself and adds
    all elements in the expansion to the list.

    This method is also a precursor to the construction of the vpd tables, since it add to every entry it encounters an attribute
    :attr:`is_vpd`, which identifies whether the given parameter/set of parameters is subject to variable packet definition or
    not. I also identifies fixed vpd repetitions from the arrays of the parameters and marks them as such.

    Args:
        h_struct (parsing.par_header.struct): The packet structure from which the parameters are to be expanded.

    Returns:
        list: List of parameters found inside the structure. Each is of type :obj:`mib_generator.parsing.par_header.misc_r`.
    """
    entries = []
    if not (type(h_struct) is int or type(h_struct) is None):
        for i in h_struct.elements:
            i.is_vpd = set()
            if i.type not in {"enum", "struct"}:
                # this is insanely ugly, but at least it shouldn't create any confusion
                if i.comment and "vpd" in i.comment[-1].entries.keys():
                    i.is_vpd.add(i.comment[-1].entries["vpd"])
                entries.append(i)
            elif i.type == "struct":
                occurences = 1
                from_struct = []
                if evalu(i.array) > 0:
                    occurences = evalu(i.array)
                if i.comment and "vpd" in i.comment[-1].entries.keys():
                    occurences = 1
                    vpd = True
                else:
                    vpd = False
                for k in range(occurences):
                    if type(i.form) is str:
                        name = i.form
                        for l in load.TmH.structures + load.TcTmH.structures:
                            if l.name == name:
                                from_struct = [copy(x) for x in h_analysis(l)]
                    else:
                        from_struct = [copy(x) for x in h_analysis(i.form)]
                if vpd:
                    for k in from_struct:
                        k.is_vpd.add(i.comment[-1].entries["vpd"])
                entries = entries + from_struct

    return entries


def var_get(entries):
    """Extract variable parameters from list of all parameters.

    This method goes through all entries in the given list and marks position of the entries which are subject to
    variable packet definition. If it encounters a case of a fixed repetition, it marks its negation (index of) position
    instead.

    Args:
        entries (list): List of parameters to be searched for vpd. Each of type :obj:`mib_generator.parsing.par_header.misc_r`.

    Returns:
        list: List of indices (or their negations in case of fixed repetitions) at which vpd parameters were found.
    """
    var = []
    for i in range(len(entries)):
        if entries[i].is_vpd:
            if "fixed" in entries[i].is_vpd:
                var.append(-i)
            var.append(i)
    return var


def count_size(entries):
    """Counts bit size of the packet and bit position of entries within it.

    Goes through the given list of parameters, for each one evaluates its bite-size and from it counts the total byte-size
    of the whole list and bite-positions of start of each parameter within it.

    Args:
        entries (list): List of parameters who's length is to be determined. Each of type :obj:`mib_generator.parsing.par_header.misc_r`.

    Returns:
        tuple: A tuple consisting of:

            * *int* - Byte-length of the list of parameters.
            * *list* - List o offset positions (in bites) of the parameters from the list start.
    """
    size_bites = 0
    positions = []
    sizes = longdata.sizes
    for i in entries:
        positions.append(size_bites)
        if i.bites != -1:
            size_bites += i.bites
        else:
            array = 1
            if evalu(i.array) != -1:
                array = evalu(i.array)
            try:
                size_bites += array * (sizes[i.type])
            except:
                print("Unknown size of type " + i.type)
    return int(size_bites / 8), positions + [size_bites]


def pi_sid(entries, positions):
    """Extract position of additional identification field from packet entries.

    This method looks the presence/position of the first additional identification field (which is recognised by the entry ``"sid"`` in its
    comments) in the packet, and if it finds it, calculates its width (in bites) and offset position (in bytes) from
    the start of the packet.

    Args:
        entries (list): List of entries (of type :obj:`mib_generator.parsing.par_header.misc_r`) among which the additional identification field
            is searched for.
        positions (list): List of position (bite-offests from the start of the packet) of the parameters in the packet.

    Returns:
        tuple: A tuple consisting of:

            * *int* - Start position (in bytes from the start of the packet) of the additional identification field.
            * *int* - Bite-width of the additional identification field.
    """
    start = None
    width = 0
    for i in range(len(entries)):
        if entries[i].comment and "sid" in entries[i].comment[0].entries.keys() and entries[i].comment[0].entries["sid"]:
            start = int(positions[i] / 8)
            width = positions[i + 1] - positions[i]
    return start, width
