"""Methods for generation of MIB tables and checking of their validity.

This module holds methods that help with generation, checking and saving of MIB tables from previously created Python 
representations of Tm/Tc packets, calibrations, etc..
"""

import mib_generator.data.longdata as longdata
import mib_generator.data.warn as warn
import mib_generator.parsing.load as load


def list_to_mib(lis):
    """Convert a 2D list of values into a string formatted as MIB ASCII file.

    From a 2D list (list in list) this functions creates one string by joining all the entries with a junction \\\\\ n for entries
    in the "1D" list and with \\\\\ t for the "nested" entries.

    Args:
        lis (list): A 2D list (list of lists) to be joined into one string.

    Returns:
        str: A string which is created from the 2D list and is formatted as an MIB database.
    """
    rowstr = []
    for row in lis:
        rowstr.append("\t".join(row))
    out = "\n".join(rowstr)
    return out


def save_mib(mib, name):
    """Save the string-MIB database into the specified folder.

    This function saves the passed string into a file named with the passed name (+.dat ending) at the location specified in
    :obj:`mib_generator.parsing.load.out_dir`.

    Args:
        mib (str): The string to be saved into a file
        name (str): Name of the file (+.dat) the string will be saved into.
    """
    path = load.out_dir + "/" + name + ".dat"
    fil = open(path, "w")
    fil.write(mib)
    fil.close()


def check(value, typ):
    """Check whether the given value matches the given type.

    This method checks whether the passed value matches the passed type (either integer number or ASCII string without a few
    characters).

    Args:
        value (str): Value who's type is to be checked.
        typ (str): The type the value should have.

    Returns:
        bool: ``True`` if the value matches the type, ``False`` otherwise.
    """
    if len(value) > typ[1]:
        return False
    if typ[0] == "n":
        try:
            x = int(value)
        except:
            return False
    if typ[0] == "c":
        if (not value.isascii()) or bool({'"', "&", "<", ">"} & set(value)):
            return False
    return True


def delete_empty(table):
    """Delete empty entries in arrays.

    This function goes through list of dictionaries to be made into MIB tables, and removes every empty (equal to ``""``) entry
    it finds. This is done so that the later tests trigger appropriate warnings.

    Args:
        table (list): List of dictionaries, each one representing a row of an MIB table, which is to be cleaned from empty
            entries.
    """
    for i in range(len(table)):
        dic = {}
        for l in table[i]:
            if table[i][l] not in {"", None}:
                dic[l] = table[i][l]
        table[i] = dic


def exclude_repetition(table, typ):
    """Exclude repetition in columns where there should be unique entries.

    This function checks whether there is any repetition in columns where entries should be unique in the passed MIB table
    and if so, deletes the additional rows and raises a warning. (the required uniqueness of entries for a given MIB table
    is defined in :obj:`mib_generator.data.longdata.unique_entries`)

    Args:
        table (list): List of dictionaries which represents the MIB database to be checked for repetition.
        typ (str): The name of the MIB database the passed table adheres to.
    """
    constraints = longdata.unique_entries[typ]
    redundance = set()
    for i in constraints:
        bare_table = []
        for l in table:
            bare_table.append([l[x - 1] for x in i])
        for x in range(len(bare_table)):
            for y in range(len(bare_table)):
                if (
                    bare_table[x] == bare_table[y]
                    and y > x
                    and "".join(bare_table[x]) != ""
                ):
                    redundance.add(y)
    if redundance:
        stradd = "\n\tThe content of these rows is:"
        for i in redundance:
            stradd = stradd + "\n\t" + str(table[i])
        warn.raises("WGM1", typ, str(redundance)[1:-1], stradd)
    indexes = sorted(list(redundance), reverse=True)
    for i in indexes:
        table.pop(i)


def pic_filter(packets):
    """Check whether the information saved in the list of Tm-packet is self-consistent and prune it for generation of pic.

    This function is an ad-hoc filter, that accounts for the fact that pic table has to have fewer entries than pid or other
    similar tables because of the fact that one entry in it corresponds only to one combination of packet type/subtype.
    However for a set of packets to be reducible to this single entry in pic, it has to be the case that they all share the
    same declaration of additional identification fields which set them apart but have the same position relative to the packet
    structure. This is hence also something that this filter checks and raises a warning whenever it encounters something
    suspicious. Finally it deletes all (valid) repetition in types/subtypes it finds, so that pic table can be directly
    generated from the output list of packets without raising further exceptions.

    Args:
        packets (list):
            List of representations of Tm-packets, each of type :obj:`mib_generator.construction.TM_packet.TM_packet`.
            This list corresponds to the pid table.

    Returns:
        list:
            List of representations of Tm-packets, each of type :obj:`mib_generator.construction.TM_packet.TM_packet`
            This list corresponds to the pic table.

    """
    repete = set()
    for x in range(len(packets)):
        for y in range(x + 1, len(packets)):
            x1 = packets[x].pic["PIC_TYPE"]
            x2 = packets[x].pic["PIC_STYPE"]
            x3 = packets[x].pic["PIC_PI1_OFF"]
            x7 = packets[x].pic["PIC_APID"]
            y1 = packets[y].pic["PIC_TYPE"]
            y2 = packets[y].pic["PIC_STYPE"]
            y3 = packets[y].pic["PIC_PI1_OFF"]
            y7 = packets[y].pic["PIC_APID"]
            if (x1, x2, x7) == (y1, y2, y7):
                if x3 != y3:
                    warn.raises(
                        "WGM2",
                        str(packets[x].pid["PID_SPID"]),
                        str(packets[y].pid["PID_SPID"]),
                    )
                elif {-1, "-1"} & {x3, y3}:
                    warn.raises(
                        "WGM3",
                        str(packets[x].pid["PID_SPID"]),
                        str(packets[y].pid["PID_SPID"]),
                    )
                else:
                    repete.add(y)
    filtered_packets = []
    for i in range(len(packets)):
        if i not in repete:
            filtered_packets.append(packets[i])
    return filtered_packets

def mnemon_check(packets, typ):
    """Check whether mnemonics for the set of passed packets and the given table are unique and existent.
    
    This follows additional mib specifications by OHB Italia, which requires special mnemonic parameter to be
    saved into the description field for a few mib tables. The mnemonics are specified to be unique and present, which is what
    this method checks and raises warning if they aren't.
    
    Args:
        packets (list): List of packets/commands. Each either of type :obj:`mib_generator.construction.TM_packet.TM_packet`
            or :obj:`mib_generator.construction.TC_packet.TC_packet`.
        typ (str): The name of the MIB table for which this is checked.
    """
    lis = set()
    repeat = set()
    for i in packets:
        dic = i.__dict__[typ]
        if type(dic) == dict:
            try:
                mnem = dic[typ.upper()+"_DESCR2"]
            except:
                mnem = None
            if mnem in lis:
                repeat.add(mnem)
            elif mnem is not None:
                lis.add(mnem)
        elif type(dic) == list:
            for k in dic:
                try:
                    mnem = k[typ.upper()+"_DESCR2"]
                except:
                    mnem = None
                if mnem in lis:
                    repeat.add(mnem)
                elif mnem is None:
                    repeat.add("")
                else:
                    lis.add(mnem)
                
    if repeat:
        stradd = "\n\tThe repeating mnemonics are:\n\t"+str(repeat)
        warn.raises("WGM6", typ, stradd)

def generate(table_type, source):
    """From a list of dictionaries (per rows) generate a MIB table of a given type.

    This function generates and saves the MIB database in the following steps:

        1. Based on the passed MIB table name, looks up what entries/columns the generated table should have
           (it takes this information from :obj:`mib_generator.data.longdata.tables_format`).
        2. From the passed list of dictionaries it creates a 2D list (list of lists) mirroring the structure of the MIB table.
        3. While doing that it runs some checks of type and uniqueness of the entries.


    Args:
        table_type (str): The name of the MIB database the passed table adheres to.
        table (list): List of dictionaries which correspond to the rows of the MIB table with the appropriate entries.

    Returns:
        list: A 2D list (list of lists) representing the generated MIB table
    """
    columns = longdata.tables_format[table_type]
    table = []
    row_ind = 1
    for i in source:
        row = []
        for l in columns:
            if l["name"] in i.keys():
                val = str(i[l["name"]])
                row.append(val)
                if not check(val, l["type"]):
                    stradd = "\n\tValue: " + str(val) + "; Type: " + str(l["type"])
                    warn.raises("WGM4", table_type, l["name"], str(row_ind), stradd)

            else:
                row.append("")
                if l["mandatory"]:
                    warn.raises("WGM5", table_type, l["name"], str(row_ind))

        table.append(row)
        row_ind += 1
    exclude_repetition(table, table_type)
    return table


def one_generate(lists, name):
    """Generate MIB database of the given name from the passed list of objects.

    This method does a few precursor steps to the generation process. For each of the objects in the passed list, it
    extracts the appropriate dictionary corresponding to the row in the MIB table associated to the object and appends this
    dictionary (alias row) to a list of all rows for this table. It then passes the resulting list through a "filter" which
    erases all entries left empty (method :obj:`delete_empty`) and calls the main generation method :obj:`generate` with
    this list.

    Args:
        lists (list): List of the objects (these can be of many types) the rows of the MIB tables (as dictionaries) are
            associated to.
        name (str): Name of the MIB table that is to be generated from these objects.

    Returns:
        list: A 2D list (list of lists) representing the generated MIB table
    """
    rows = []
    for i in lists:
        rows.append(vars(i)[name])
    delete_empty(rows)
    return generate(name, rows)


def two_generate(lists, name):
    """Generate MIB database of the given name from the passed list of objects.

    This method does a few precursor steps to the generation process. For each of the objects in the passed list, it
    extracts the appropriate dictionaries (in a list) corresponding to the rows in the MIB table associated to the object
    and appends these dictionaries (alias rows) to a list of all rows for this table. It then passes the resulting list
    through a "filter" which erases all entries left empty (method :obj:`delete_empty`) and calls the main generation
    method :obj:`generate` with this list.

    Args:
        lists (list): List of the objects (these can be of many types) the rows of the MIB tables (as dictionaries) are
            associated to.
        name (str): Name of the MIB table that is to be generated from these objects.

    Returns:
        list: A 2D list (list of lists) representing the generated MIB table
    """
    rows = []
    rows = []
    for i in lists:
        for l in vars(i)[name]:
            rows.append(l)
    delete_empty(rows)
    return generate(name, rows)
