"""Methods for creation of TC MIB tables and internal representation of TC command packets in general.

This module holds methods that help with formatting of parsed data into TC packet and commands characteristics. They are usually
concerned with value evaluation, bite counting, type identification etc. I.e. mostly kind of housekeeping jobs.
"""
from copy import copy

import mib_generator.data.warn as warn
import mib_generator.parsing.load as load
from mib_generator.construction.TM_packet_methods import (
    categfromptc,
    count_size,
    evalu,
    getptcpcf,
)


def find_header(file):
    """Find structure in this file which describes a TC header.

    Based on its name, find a structure which corresponds to a TC header. Otherwise return a warning.

    Args:
        file (parsing.parser_main.file): File (in Python representation) which is searched for the header.

    Returns:
        parsing.par_cfile.struct: The structure identifies as the header.
    """
    for i in file.structures:
        if "name" in i.__dir__() and i.name == "TcHead":
            return i
    warn.raises("WCT1")


def packet_search(file):
    """Extract individual TC-command definitions from TC-header file.

    Search the inputted file for TC-command definition using their preceding description comments and return
    them in a list.

    This is needed because unlike for TM-packets where the list of all packets is predefined in the TM ``.c`` file,
    here all packets' definitions have to be found in the first place.

    Args:
        file (:obj:`mib_generator.parsing.parser_main.file`): File (in Python representation) which is searched for the command definitions.

    Returns:
        list: List of command definition structures found in the file. Each an instance of :obj:`mib_generator.parsing.par_header.struct`
    """
    packets = []
    for i in file.structures:
        if (
            i.type == "struct"
            and i.comment
            and "packet" in i.comment[-1].entries.keys()
        ):
            packets.append(i)
    return packets


def h_analysis(h_struct):
    """Make a list of all individual (all structs unpacked) entries in the command.

    This method goes iteratively through all entries/parameters inside the given structure. If it finds a normal entry,
    it adds it to the list, if it finds a ``struct`` or reference to one, it expands it by recursively calling itself and adds
    all elements in the expansion to the list.

    Furthermore here, two output lists are created, one including all parameters from the TC-packet header and the other one
    including all parameters relating to the actual command.

    Args:
        h_struct (parsing.par_header.struct): The packet structure from which the parameters are to be expanded.

    Returns:
        tuple: A tuple consisting of:

            * *list* - List of parameters found inside the structure relating to the packet header. Each is of type
              :obj:`mib_generator.parsing.par_header.misc_r`.
            * *list* - List of parameters found inside the structure relating to the command content. Each is of type
              :obj:`mib_generator.parsing.par_header.misc_r`.
    """
    entries_head = []
    entries = []
    if not (type(h_struct) is int or type(h_struct) is None):
        for i in h_struct.elements:
            if i.type not in {"enum", "struct"}:
                entries.append(i)
            elif i.type == "struct":
                occurences = 1
                from_struct = []
                if evalu(i.array) > 0:
                    occurences = evalu(i.array)
                for k in range(occurences):
                    if type(i.form) is str:
                        name = i.form
                        for l in load.TcH.structures + load.TcTmH.structures:
                            if l.name == name:
                                from_struct = [copy(x) for x in h_analysis(l)[1]]
                    else:
                        from_struct = [copy(x) for x in h_analysis(i.form)[1]]
                if i.name not in {"SpwHead", "TcHead"}:
                    entries = entries + from_struct
                else:
                    entries_head = entries_head + from_struct
    return entries_head, entries


def get_gr_sizes(entries):
    """Get sizes of (repeting) groups of command entries.

    Based on comments attached to each entry/parameter this method decides whether it is part of a repeating group or not and if so
    whether it is a "data" or "count" parameter. It then marks positions of such groups and creates a list of corresponding group-sizes
    where position of each counter corresponds to a group size and the remaining entries are left 0.

    Args:
        entries (list): List of entries which are to be analysed for command groups. Each of type :obj:`mib_generator.parsing.par_header.misc_r`.

    Returns:
        list: List parallel to the inputted one with "counter" parameters having the value of their group-sizes and all other values are ``0``.
    """
    counter = 0
    sizes = []
    for i in range(len(entries)):
        entry = entries[-i - 1]
        if entry.comment and "cdf" in entry.comment[-1].entries.keys():
            if entry.comment[-1].entries["cdf"] == "count":
                sizes.append(counter)
                # Here there could be also = 0, then repeated sub-groups would not be possible.
                counter += 1
            else:
                sizes.append(0)
                counter += 1
        else:
            sizes.append(0)
            counter = 0
    sizes.reverse()
    return sizes


def param_list(entries):
    """Get list of parameters in command entries and their positions in the cpc table.

    Based on their name (if it is not ``"spare"``) this method decides whether a given entry in a command definition is a parameter or a
    fixed area. It then creates a list in which parameters are marked by their original index and fixed areas by ``-1``.

    Args:
        entries (list): List of entries which are to be analysed. Each of type :obj:`mib_generator.parsing.par_header.misc_r`.
    Returns:
        list: List parallel to the inputted one with parameters having the value of their index and fixed areas a value of ``-1``.
    """
    params = []
    ind = 0
    for i in range(len(entries)):
        if entries[i].name != "spare":
            params.append(ind)
            ind += 1
        else:
            params.append(-1)
    return params
