"""Module holding Python representations of TC packets, TC header and the corresponding MIB tables.

This module takes care of creating a representation of TC commands from parsed sections of C-files and extracting 
entries for MIB databases. These classes represent the TC commands only in the sense that they hold in a structured
form any possible information that could be found relating to that command including the entries in various MIB tables that
correspond to it.
"""
import mib_generator.construction.TC_packet_methods as pm
import mib_generator.parsing.load as load


class TC_header:
    """Class representing the TC header common to all TC-packets.

    This class is an abstract representation of a TC packet header with all of its properties, entries and corresponding MIB tables.
    It is created from passed :obj:`mib_generator.parsing.par_header.struct` object and and subsequently analysed using included methods into
    the entries in various TC-side MIB tables.

    Args:
        structure (parsing.par_cfile.struct):  An object corresponding to a description of this packet-header found in the
            :obj:`mib_generator.parsing.load.TcH` file (i.e. the TC ``.h`` file).

    Attributes:
        structure (parsing.par_cfile.struct): An object corresponding to a description of this packet found in the
            :obj:`mib_generator.parsing.load.TcH` file (i.e. the TC ``.h`` file).
        entries (list): List of entries found inside the TC-header. Each is an instance of :obj:`mib_generator.parsing.par_header.misc_r`.
        size (int): Size of the packet header (joint size of all its entries) in bytes.
        positions (list): List of starting positions of entries in the TC-header packet. Each entry is an integer representing an
            offset from the header start.
        tcp (dict): Dictionary corresponding to one line in MIB tcp table.
        pcpc (list): List of dictionaries each one corresponding to one line in MIB pcpc table.
        pcdf (list): List of dictionaries each one corresponding to one line in MIB pcdf table.
    """

    def __init__(self, structure):
        self.structure = structure
        self.entries = pm.h_analysis(self.structure)[1]
        self.size, self.positions = pm.count_size(self.entries)
        self.parameters = pm.param_list(self.entries)
        self.tcp = self.tcp_dictionary()
        self.pcpc = self.pcpc_listdict()
        self.pcdf = self.pcdf_listdict()

    def tcp_dictionary(self):
        """Define elements for entry in tcp table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the tcp table (with the key being
        the name of the column and value the entry to be filled in). Here the values are extracted from the comment preceding the
        TC-header definitions.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`tcp`.
        """
        diction = {}
        try:
            diction["TCP_ID"] = self.structure.comment[-1].entries["text_id"]
        except:
            diction["TCP_ID"] = self.structure.name
        try:
            diction["TCP_DESC"] = self.structure.comment[-1].entries["desc"]
        except:
            diction["TCP_DESC"] = ""
        return diction

    def pcpc_listdict(self):
        """Define elements for entries in pcpc table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the pcpc table (with
        the key being the name of the column and value the entry to be filled in). Here for each parameter in the header, one row
        (i.e. one entry in the list) is created, entries in which are extracted from comments around the given parameter, calculated
        from type/general information, etc...

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`pcpc`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            if self.parameters[i] >= 0:
                diction = {}
                try:
                    no = "{:X}".format(
                        int(
                            str(self.structure.comment[-1].entries["base_par_index"]),
                            16,
                        )
                        + i
                    )
                    diction["PCPC_PNAME"] = self.structure.comment[-1].entries[
                        "prefix"
                    ] + str(no)
                except:
                    diction["PCPC_PNAME"] = self.entries[i].name
                try:
                    diction["PCPC_DESC"] = self.entries[i].comment[-1].entries["desc"]
                except:
                    diction["PCPC_DESC"] = ""
                if self.entries[i].type[:4] in {"unit", "unsi"}:
                    diction["PCPC_CODE"] = "U"
                else:
                    diction["PCPC_CODE"] = "I"
                entrydict.append(diction)
        return entrydict

    def pcdf_listdict(self):
        """Define elements for entries in pcdf table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the pcdf table (with
        the key being the name of the column and value the entry to be filled in). Here for each parameter in the header, one row
        (i.e. one entry in the list) is created, entries in which are mostly deduced from the parameter's name or position/width.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`pcdf`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            diction = {}
            diction["PCDF_TCNAME"] = self.tcp["TCP_ID"]
            diction["PCDF_DESC"] = self.pcpc[self.parameters[i]]["PCPC_DESC"]
            match self.entries[i].name:
                case "apid":
                    diction["PCDF_TYPE"] = "A"
                case "serviceType":
                    diction["PCDF_TYPE"] = "T"
                case "subType":
                    diction["PCDF_TYPE"] = "S"
                case _:
                    if self.parameters[i] < 0:
                        diction["PCDF_TYPE"] = "F"
                    else:
                        diction["PCDF_TYPE"] = "P"
            diction["PCDF_LEN"] = int(self.positions[i + 1] - self.positions[i])
            diction["PCDF_BIT"] = self.positions[i]
            if diction["PCDF_TYPE"] != "F":
                diction["PCDF_PNAME"] = self.pcpc[self.parameters[i]]["PCPC_PNAME"]
            # There should definitely be some default values here.
            # diction["PCDF_VALUE"] = ""
            # diction["PCDF_RADIX"] = ""
            entrydict.append(diction)
        return entrydict


class TC_packet:
    """Class representing a TC-packet/command and its various properties.

    This class is an abstract representation of a TC command with all of its properties, entries and corresponding MIB tables.
    It is created from passed :obj:`mib_generator.parsing.par_header.struct` and :obj:`TC_header` objects and and subsequently analysed using
    included methods into the entries in various TC-side MIB tables.

    Args:
        h_structure (parsing.par_header.struct):  An object corresponding to a description of this command found in the
            :obj:`mib_generator.parsing.load.TcH` file (i.e. the TC ``.h`` file).
        header (TC_header): A TC-header included at the start of the packet in which the command in question is send.

    Attributes:
        h_structure (parsing.par_header.struct):  An object corresponding to a description of this command found in the
            :obj:`mib_generator.parsing.load.TcH` file (i.e. the TC ``.h`` file).
        header (TC_header): A TC-header included at the start of the packet in which the command in question is send.
        h_entries (list): List of entries that relate to the header found inside the command definition. Each is an instance of
            :obj:`mib_generator.parsing.par_header.misc_r`.
        entries (list): List of entries that do not relate to the headerfound inside the command definition. Each is an instance
            of :obj:`mib_generator.parsing.par_header.misc_r`.
        size (int): Size of the command definition (joint size of all parameters in :attr:`entries`) in bytes.
        positions (list): List of starting positions of :attr:`entries` in the command definition. Each entry is an integer representing an
            offset from the start.
        h_size (int): Size of the command definition (joint size of all parameters in :attr:`h_entries`) in bytes.
        h_positions (list): List of starting positions of :attr:`h_entries` in the command definition. Each entry is an integer representing an
            offset from the start.
        parameters (list): List of indexes of all parameters in :attr:`entries` (i.e. those that aren't fixed areas). If entry is a parameter,
            the corresponding field in this list has its index value, otherwise it is assigned -1.
        ccf (dict): Dictionary corresponding to one line in MIB ccf table.
        cpc (list): List of dictionaries each one corresponding to one line in MIB cpc table.
        cdf (list): List of dictionaries each one corresponding to one line in MIB cdf table.
        prf (list): List of dictionaries each one corresponding to one line in MIB prf table.
        prv (list): List of dictionaries each one corresponding to one line in MIB prv table.
        cvp (list): List of dictionaries each one corresponding to one line in MIB cvp table.
    """

    def __init__(self, h_structure, header):
        self.h_structure = h_structure
        self.header = header
        self.h_entries, self.entries = pm.h_analysis(self.h_structure)
        self.size, self.positions = pm.count_size(self.entries)
        self.h_size, self.h_position = pm.count_size(self.h_entries)
        self.parameters = pm.param_list(self.entries)
        self.ccf = self.ccf_dictionary()
        self.cpc = self.cpc_listdict()
        self.cdf = self.cdf_listdict()
        self.prf = self.prf_listdict()
        self.prv = self.prv_listdict()
        self.cvp = self.cvp_listdict()

    def ccf_dictionary(self):
        """Define elements for entry in ccf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the ccf table (with the key being
        the name of the column and value the entry to be filled in). Here the values are mostly general information extracted
        from the comment in from of the command definition in the C-header file and such.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`ccf`.
        """
        diction = {}
        try:
            diction["CCF_CNAME"] = self.h_structure.comment[-1].entries["text_id"]
        except:
            diction["CCF_CNAME"] = ""
        try:
            diction["CCF_DESCR"] = self.h_structure.comment[-1].entries["desc"]
        except:
            diction["CCF_DESCR"] = ""
        try:
            diction["CCF_DESCR2"] = self.h_structure.comment[-1].entries["Mnemonic"]
        except:
            diction["CCF_DESCR2"] = ""
        # diction["CCF_CTYPE"] = ""
        # diction["CCF_CRITICAL"] = ""
        diction["CCF_PKTID"] = self.header.tcp["TCP_ID"]
        try:
            diction["CCF_TYPE"] = self.h_structure.comment[-1].entries["service"]
            diction["CCF_STYPE"] = self.h_structure.comment[-1].entries["sub"]
        except:
            diction["CCF_TYPE"] = ""
            diction["CCF_STYPE"] = ""
        # diction["CCF_APID"] = ""
        diction["CCF_NPARS"] = len(self.entries)
        # diction["CCF_PLAN"] = ""
        # diction["CCF_EXEC"] = ""
        # diction["CCF_ILSCOPE"] = ""
        # diction["CCF_ILSTAGE"] = ""
        # diction["CCF_SUBSYS"] = ""
        # diction["CCF_HIPRI"] = ""
        # diction["CCF_MAPID"] = ""
        # diction["CCF_DEFSET"] = ""
        # diction["CCF_RAPID"] = ""
        # diction["CCF_ACK"] = ""
        # diction["CCF_SUBSCHEDID"] = ""
        return diction

    def cpc_listdict(self):
        """Define elements for entries in cpc table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the pcpc table (with
        the key being the name of the column and value the entry to be filled in). Here for each parameter in the header, one row
        (i.e. one entry in the list) is created, entries in which are extracted from comments around the given parameter, calculated
        from type/general information, etc... It should be mentioned that not all entries in :attr:`etnries` are parameters since they
        can be also fixed areas. Hence first, before the dictionary is created, a check is run for this.

        Unusual case here is the range check ``"CPC_PRFREF"``. Normal here would be to directly associate it to some externally defined
        calibration, but since that would be quite convoluted and ineffective for such simple task, it was decided to generate a random
        placeholder name (rather than predefined one) to be put into the ``"CPC_PRFREF"`` entry and then generate the range check tables
        as an attribute of this command class :attr:`prf` and :attr:`prv` (rather then as an external object as is the case with all
        other calibrations).

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`cpc`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            if self.parameters[i] >= 0:
                diction = {}
                size = int(self.positions[i + 1] - self.positions[i])
                try:
                    no = "{:X}".format(
                        int(
                            str(self.h_structure.comment[-1].entries["base_par_index"]),
                            16,
                        )
                        + i
                    )
                    diction["CPC_PNAME"] = self.h_structure.comment[-1].entries[
                        "prefix"
                    ] + str(no)
                except:
                    diction["CPC_PNAME"] = ""
                try:
                    diction["CPC_DESCR"] = self.entries[i].comment[-1].entries["desc"]
                except:
                    diction["CPC_DESCR"] = ""
                diction["CPC_PTC"], diction["CPC_PFC"] = pm.getptcpcf(
                    self.entries[i], size
                )
                try:
                    if {"cal", "enum"} & self.entries[i].comment[-1].entries.keys():
                        diction["CPC_CATEG"] = "T"
                    else:
                        diction["CPC_CATEG"] = ""
                except:
                    diction["CPC_CATEG"] = ""
                if diction["CPC_CATEG"] == "T":
                    diction["CPC_DISPFMT"] = "A"
                elif diction["CPC_PTC"] == 9:
                    diction["CPC_DISPFMT"] = "T"
                elif diction["CPC_PTC"] == 10:
                    diction["CPC_DISPFMT"] = "D"
                else:
                    diction["CPC_DISPFMT"] = "U"
                # diction["CPC_RADIX"] = ""
                try:
                    diction["CPC_UNIT"] = self.entries[i].comment[-1].entries["unit"]
                except:
                    diction["CPC_UNIT"] = ""
                if (
                    self.entries[i].comment
                    and {"min", "max"} & self.entries[i].comment[-1].entries.keys()
                ):
                    # generate pseudo-random name for the range check
                    diction["CPC_PRFREF"] = "RAN" + str(hash(diction["CPC_PNAME"]))[-7:]
                else:
                    diction["CPC_PRFREF"] = ""
                # diction["CPC_CCAREF"] = ""
                if (
                    self.entries[i].comment
                    and "enum" in self.entries[i].comment[-1].entries.keys()
                ):
                    diction["CPC_PAFREF"] = self.entries[i].comment[-1].entries["enum"]
                else:
                    diction["CPC_PAFREF"] = ""
                # diction["CPC_INTER"] = ""
                # diction["CPC_DEFVAL"] = ""
                # diction["CPC_CORR"] = ""
                # diction["CPC_OBTID"] = ""
                try:
                    diction["CPC_DESCR2"] = self.entries[i].comment[-1].entries["Mnemonic"]
                except:
                    diction["CPC_DESCR2"] = ""
                # diction["CPC_ENDIAN"] = ""
                entrydict.append(diction)
        return entrydict

    def cdf_listdict(self):
        """Define elements for entries in cdf table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the cdf table (with
        the key being the name of the column and value the entry to be filled in). Here for each parameter in the header, one row
        (i.e. one entry in the list) is created, entries in which are mostly deduced from the parameter's name or position/width.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`cdf`.
        """
        entrydict = []
        gr_size = pm.get_gr_sizes(self.entries)
        for i in range(len(self.entries)):
            size = int(self.positions[i + 1] - self.positions[i])
            diction = {}
            diction["CDF_CNAME"] = self.ccf["CCF_CNAME"]
            if self.parameters[i] < 0:
                diction["CDF_ELTYPE"] = "A"
            else:
                diction["CDF_ELTYPE"] = "E"
            try:
                diction["CDF_DESCR"] = self.entries[i].comment[-1].entries["desc"]
            except:
                diction["CDF_DESCR"] = ""
            diction["CDF_ELLEN"] = size
            diction["CDF_BIT"] = self.positions[i]
            diction["CDF_GRPSIZE"] = gr_size[i]
            if diction["CDF_ELTYPE"] in {"E", "F"}:
                diction["CDF_PNAME"] = self.cpc[self.parameters[i]]["CPC_PNAME"]
            else:
                diction["CDF_PNAME"] = ""
            # diction["CDF_INTER"] = ""
            if diction["CDF_ELTYPE"] != "A":
                try:
                    diction["CDF_VALUE"] = pm.evalu(
                        self.entries[i].comment[-1].entries["default"]
                    )
                except:
                    diction["CDF_VALUE"] = ""
            else:
                try:
                    diction["CDF_VALUE"] = pm.evalu(
                        self.entries[i].comment[-1].entries["default"]
                    )
                except:
                    diction["CDF_VALUE"] = 0
            # diction["CDF_TMID"] = ""
            entrydict.append(diction)
        return entrydict

    def prf_listdict(self):
        """Define elements for entries in prf table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the prf table (with
        the key being the name of the column and value the entry to be filled in). Here it is first checked whether the given
        parameter has a range associated to it and if so appropriate entries for name of the parameter and ad-hoc calibration
        are generated.

        For a reason why this table is here see :obj:`cpc_listdict`.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`prf`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            if self.parameters[i] >= 0 and self.cpc[self.parameters[i]]["CPC_PRFREF"]:
                diction = {}
                diction["PRF_NUMBR"] = self.cpc[self.parameters[i]]["CPC_PRFREF"]
                # diction["PRF_DESCR"] = ""
                # diction["PRFINTER"] = ""
                # diction["PRF_DSPFMT"] = ""
                # My code assumes that the bellow is decimal, but that is the default value anyways
                # diction["PRF_RADIX"] = ""
                diction["PRF_NRANGE"] = len(
                    {"min", "max"} & self.entries[i].comment[-1].entries.keys()
                )
                diction["PRF_UNIT"] = self.cpc[self.parameters[i]]["CPC_UNIT"]
                entrydict.append(diction)
        return entrydict

    def prv_listdict(self):
        """Define elements for entries in prv table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the prv table (with
        the key being the name of the column and value the entry to be filled in). Here it is first checked whether the given
        parameter has a range associated to it and if so, the entries for the corresponding ad-hoc calibration are created.

        For a reason why this table is here see :obj:`cpc_listdict`.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`prv`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            if self.parameters[i] >= 0 and self.cpc[self.parameters[i]]["CPC_PRFREF"]:
                diction = {}
                diction["PRV_NUMBR"] = self.cpc[self.parameters[i]]["CPC_PRFREF"]
                try:
                    diction["PRV_MINVAL"] = pm.evalu(
                        self.entries[i].comment[-1].entries["min"]
                    )
                except:
                    diction["PRV_MINVAL"] = 0
                try:
                    diction["PRV_MAXVAL"] = pm.evalu(
                        self.entries[i].comment[-1].entries["max"]
                    )
                    if diction["PRV_MAXVAL"] == -1:
                        diction["PRV_MAXVAL"] = diction["PRV_MINVAL"]
                except:
                    diction["PRV_MAXVAL"] = ""
                entrydict.append(diction)
        return entrydict

    def cvp_listdict(self):
        """Define elements for entries in cvp table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the cvp table (with
        the key being the name of the column and value the entry to be filled in). First checks whether there are verifications associated
        to the given command and if so, creates an entry row to each one of them.

        There are default values for verification which are applied automatically later for each command if no verification are specified here
        (in which case the value of :attr:`cvp` will be ``None`` for now).

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`cvp`.
        """
        if (
            self.h_structure.comment
            and "cvs" in self.h_structure.comment[-1].entries.keys()
        ):
            entrydict = []
            for i in self.h_structure.comment[-1].entries["cvs"]:
                diction = {}
                diction["CVP_TASK"] = self.ccf["CCF_CNAME"]
                diction["CVP_TYPE"] = "C"
                diction["CVP_CVSID"] = i
                entrydict.append(diction)
            return entrydict
        else:
            return None
