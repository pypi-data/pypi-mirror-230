"""Module holding Python representations of TM packets, TM header and the corresponding MIB tables.

This module takes care of creating a representation of monitoring packets from parsed sections of C-files and extracting 
entries for MIB databases. These classes represent the monitoring packets only in the sense that they hold in a structured
form any possible information that could be found relating to that packet including the entries in various MIB tables that
correspond to it.
"""
import mib_generator.construction.TM_packet_methods as pm
import mib_generator.data.warn as warn


class TM_header:
    """Class representing the TM header common to all TM-packets.

    This class holds information about the TM header which is common to all TM packets. It is first found in the parsed
    C-code using the :obj:`find_header` method and then using methods from :obj:`TM_packet_methods` its entries are recognised
    and analysed:

    Args:
        file (parsing.parser_main.file): A parsed representation of the file in which the header is to be found.

    Attributes:
        structure (parsing.par_header.struct): The structure found in the header file (in its Python representation)
            which describes the common TM header.
        entries (list): List of entries found inside the TM header. Each is an instance of :obj:`mib_generator.parsing.par_header.misc_r`.
        size (int): Size of the whole TM header in bytes.
        positions (list): List of starting positions of entries in the TM header. Each entry is an integer representing an
            offset from the header start.
    """

    def __init__(self, file):
        self.structure = self.find_header(file)
        self.entries = pm.h_analysis(self.structure)
        self.size, self.positions = pm.count_size(self.entries)

    def find_header(self, file):
        """Find structure which describes the TM header.

        Based on its name, find a structure which corresponds to the TM header. Otherwise return a warning.

        Args:
            file (:obj:`mib_generator.parsing.parser_main.file`): File (in Python representation) which is searched for the header.

        Returns:
            :obj:`mib_generator.parsing.par_header.struct`: The structure identifies as the header.
        """
        for i in file.structures:
            methods = i.__dir__()
            if "name" in methods and i.name == "TmHead":
                return i
        warn.raises("WCT2")


class TM_packet:
    """Class representing a TM packet type and its various properties.

    This class is an abstract representation of a TM packet with all of its properties, entries and corresponding MIB tables.
    It is created from passed structures found in the :obj:`mib_generator.parsing.load.TmH` and :obj:`mib_generator.parsing.load.TmC` (Python representations
    of the two files describing telemetry packets) and subsequently using included methods analysed into the entries in various
    telemetry-side MIB tables.

    Args:
        structure (parsing.par_cfile.struct): An object corresponding to a description of this packet found in the
            :obj:`mib_generator.parsing.load.TmC` file (i.e. the telemetry ``.c`` file).
        h_structure (parsing.par_header.struct): An object corresponding to a description of this packet found in the
            :obj:`mib_generator.parsing.load.TmH` file (i.e. the telemetry ``.h`` file).
        header (TM_header): The header structure included in the packet.

    Attributes:
        structure (parsing.par_cfile.struct): An object corresponding to a description of this packet found in the
            :obj:`mib_generator.parsing.load.TmC` file (i.e. the telemetry ``.c`` file).
        h_structure (parsing.par_header.struct): An object corresponding to a description of this packet found in the
            :obj:`mib_generator.parsing.load.TmH` file (i.e. the telemetry ``.h`` file).
        header (TM_header): The header structure included in the packet.
        entries (list): List of entries found inside the TM packet. Each is an instance of :obj:`mib_generator.parsing.par_header.misc_r`.
        var_entries (list): List of entries which are subject to variable packet definition. For every such entry, the index
            of this entry (w.r.t. :attr:`entries`) is added to this list (or its negated value in case it is a fixed repetition).
        size (int): Size of the packet (joint size of all its entries) in bytes.
        positions (list): List of starting positions of entries in the TM packet. Each entry is an integer representing an
            offset from the header start.
        pid (dict): Dictionary corresponding to one line in MIB pid table.
        pic (dict): Dictionary corresponding to one line in MIB pic table.
        tpcf (dict): Dictionary corresponding to one line in MIB tpcf table.
        pcf (list): List of dictionaries each one corresponding to one line in MIB pcf table.
        plf (list): List of dictionaries each one corresponding to one line in MIB plf table.
        cur (list): List of dictionaries each one corresponding to one line in MIB cur table.
        vpd (list): List of dictionaries each one corresponding to one line in MIB vpd table.
    """

    def __init__(self, structure, h_structure, header):
        self.structure = structure
        self.header = header
        self.h_structure = h_structure
        self.entries = pm.h_analysis(self.h_structure)
        self.var_entries = pm.var_get(self.entries)
        self.size, self.positions = pm.count_size(self.entries)
        self.pid = self.pid_dictionary()
        self.pic = self.pic_dictionary()
        self.tpcf = self.tpcf_dictionary()
        self.pcf = self.pcf_listdict()
        self.plf = self.plf_listdict()
        self.cur = self.cur_listdict()
        self.vpd = self.vpd_listdict()

    def pid_dictionary(self):
        """Define elements for entry in pid table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the pid table (with the key being
        the name of the column and value the entry to be filled in). The entries here are extracted mostly from information in
        the telemetry ``.c`` file or the comment preceding the structure in the ``.h`` file.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`pid`.
        """
        diction = {}
        diction["PID_TYPE"] = pm.evalu(self.structure.entries[".serviceType"])
        diction["PID_STYPE"] = pm.evalu(self.structure.entries[".serviceSubType"])
        diction["PID_APID"] = pm.apidnum(self.structure.entries[".apid"])
        try:
            sid = [
                i.comment[-1].entries["const_value"]
                for i in self.h_structure.elements
                if i.name == "sid"
            ]
            diction["PID_PI1_VAL"] = pm.evalu(sid[0])
        except:
            diction["PID_PI1_VAL"] = "-1"
        # diction["PID_PI2_VAL"] =
        try:
            diction["PID_SPID"] = self.h_structure.comment[-1].entries["spid"]
        except:
            diction["PID_SPID"] = ""
        try:
            diction["PID_DESCR"] = self.h_structure.comment[-1].entries["desc"]
        except:
            diction["PID_DESCR"] = ""
        # diction["PID_UNIT"] =
        if self.var_entries:
            diction["PID_TPSD"] = diction["PID_SPID"]
        else:
            diction["PID_TPSC"] = "-1"
        # I'm not very sure this is actually what DFHSIZE is supposed to be.
        diction["PID_DFHSIZE"] = self.header.size
        # diction["PID_TIME"] =
        # diction["INTER"] =
        # diction["PID_VALID"] =
        # diction["PID_CHECK"] =
        # diction["PID_EVENT"] =
        # diction["PID_EVID"] =
        return diction

    def pic_dictionary(self):
        """Define elements for entry in pic table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the pic table (with the key being
        the name of the column and value the entry to be filled in). Here most of the work is done at the search of the ``sid`` entry
        of the packet (which is done using :obj:`mib_generator.construction.TM_packet_methods.pi_sid` method) and extracting information about additional packet
        identifiers from it.

        Because of how these tables are created. I can't initially respect the requirement that there should be only one unique
        entry in the ``"PIC_TYPE"`` and ``"PIC_STYPE"`` columns. Because of this, there has to be a pruning method applied later at the generation
        step which deletes such repeating entries.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`pic`.
        """
        diction = {}
        diction["PIC_TYPE"] = self.pid["PID_TYPE"]
        diction["PIC_STYPE"] = self.pid["PID_STYPE"]
        offset, width = pm.pi_sid(self.entries, self.positions)
        if offset is not None:
            diction["PIC_PI1_OFF"] = offset + self.header.size
            diction["PIC_PI1_WID"] = width
        else:
            diction["PIC_PI1_OFF"] = -1
            diction["PIC_PI1_WID"] = 0
        try:
            diction["PIC_PI2_OFF"] = self.h_structure.comment[-1].entries["PI2"][0]
            diction["PIC_PI2_WID"] = self.h_structure.comment[-1].entries["PI2"][1]
        except:
            diction["PIC_PI2_OFF"] = -1
            diction["PIC_PI2_WID"] = 0
        diction["PIC_APID"] = self.pid["PID_APID"]
        return diction

    def tpcf_dictionary(self):
        """Define elements for entry in tpcf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the tpcf table (with the key being
        the name of the column and value the entry to be filled in). Here only text id of the packet is extracted from the
        comment preceding the packet structure in the header file.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`tpcf`.
        """
        diction = {}
        diction["TPCF_SPID"] = self.pid["PID_SPID"]
        try:
            diction["TPCF_NAME"] = self.h_structure.comment[-1].entries["text_id"]
        except:
            diction["TPCF_NAME"] = ""
        # diction["TPCF_SIZE"] =
        return diction

    def pcf_listdict(self):
        """Define elements for entries in pcf table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the pcf table (with
        the key being the name of the column and value the entry to be filled in). Here one "MIB row" is created for each entry/parameter
        in :attr:`entries` and for each row most of the information is taken from the comment attached to the line at which the C-object
        describing the entry is found in the original C-files.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`pcf`.
        """
        entrydict = []
        for i in range(len(self.entries)):
            diction = {}
            size = int(self.positions[i + 1] - self.positions[i])
            try:
                no = "{:X}".format(
                    int(str(self.h_structure.comment[-1].entries["base_par_index"]), 16)
                    + i
                )
                diction["PCF_NAME"] = self.h_structure.comment[-1].entries[
                    "prefix"
                ] + str(no)
            except:
                diction["PCF_NAME"] = ""
            try:
                diction["PCF_DESCR"] = self.entries[i].comment[-1].entries["desc"]
            except:
                diction["PCF_DESCR"] = ""
            # diction["PCF_PID"] =
            try:
                diction["PCF_UNIT"] = self.entries[i].comment[-1].entries["unit"]
            except:
                diction["PCF_UNIT"] = ""
            diction["PCF_PTC"], diction["PCF_PFC"] = pm.getptcpcf(self.entries[i], size)
            diction["PCF_WIDTH"] = size
            # diction["PCF_VALID"] =
            # diction["PCF_RELATED"] =
            diction["PCF_CATEG"] = pm.categfromptc(diction["PCF_PTC"])
            # this uses probably a wrong specification of natur
            try:
                diction["PCF_NATUR"] = self.entries[i].comment[-1].entries["natur"]
            except:
                diction["PCF_NATUR"] = "R"
            try:
                diction["PCF_CURTX"] = self.entries[i].comment[-1].entries["cal"]
            except:
                diction["PCF_CURTX"] = ""
            # diction["PCF_INTER"] =
            # diction["PCF_USCON"] =
            # diction["PCF_DECIM"] =
            # diction["PCF_PARVAL"] =
            # diction["PCF_SUBSYS"] =
            # diction["PCF_VALPAR"] =
            # diction["PCF_SPTYPE"] =
            # diction["PCF_CORR"] =
            # diction["PCF_OBTID"] =
            # diction["PCF_DARC"] =
            # diction["PCF_ENDIAN"] =
            try:
                diction["PCF_DESCR2"] = self.entries[i].comment[-1].entries["Mnemonic"]
            except:
                diction["PCF_DESCR2"] = ""
            entrydict.append(diction)
        return entrydict

    def plf_listdict(self):
        """Define elements for entries in plf table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the plf table (with
        the key being the name of the column and value the entry to be filled in). Here the information in :attr:`positions` are
        employed in order to calculates the offsets of each parameter (corresponding to an element in :attr:`entries`) from the start
        of the packet and its width in bites.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`plf`.
        """
        entrydict = []
        positions = [x + self.header.size * 8 for x in self.positions]
        for i in range(len(self.entries)):
            diction = {}
            size = positions[i + 1] - positions[i]
            diction["PLF_NAME"] = self.pcf[i]["PCF_NAME"]
            diction["PLF_SPID"] = self.pid["PID_SPID"]
            diction["PLF_OFFBY"] = int(positions[i] / 8)
            diction["PLF_OFFBI"] = positions[i] - diction["PLF_OFFBY"] * 8
            # diction["PLF_NBOCC"] = abs(pm.evalu(self.entries[i].array))
            # diction["PLF_LGOCC"] =
            # diction["PLF_TIME"] =
            # diction["PLF_TDOCC"] =
            entrydict.append(diction)
        return entrydict

    def cur_listdict(self):
        """Define elements for entries in cur table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the cur table (with
        the key being the name of the column and value the entry to be filled in). Here for each parameters it is looked up whether
        any calibrations is required (if it is defined in the corresponding comment), and if so the appropriate entry is created.

        As of now, this supports only a single calibration assigned to each parameter.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`cur`.
        """
        entrydict = []
        for l in range(len(self.entries)):
            i = self.entries[l]
            # this will have to be modified when I get how multiple calibrations will look in comments
            if i.comment and "cals" in i.comment[-1].entries.keys():
                diction = {}
                diction["CUR_PNAME"] = self.pcf[l]["PCF_NAME"]
                diction["CUR_SELECT"] = i.comment[-1].entries["cal"]
                # diction["CUR_POS"] =
                # diction["CUR_RLCHK"] =
                # diction["CUR_VALPAR"] =
                entrydict.append(diction)
        return entrydict

    def vpd_listdict(self):
        """Define elements for entries in vpd table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the vpd table (with
        the key being the name of the column and value the entry to be filled in). As the first step here, the group sizes for each
        repetition of parameters are calculated using the information in :attr:`var_entries`. Then, based on these information, for
        each of entries identified as repeting/counters in :attr:`var_entries`, a row in the vpd table is created.

        A weird subcase are fixed repetitions. Here since there has to be some counter for them to be included in the vpd table, an
        additional "virtual" entry is added to the pcf table which represents this counter but isn't included in any packet.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`vpd`.
        """
        count = []
        ind = 0
        for i in range(len(self.var_entries)):
            if self.var_entries[-i - 1] >= 0 and self.entries[
                self.var_entries[-i - 1]
            ].is_vpd == {"count"}:
                count.append(ind)
                ind = 0
            elif self.var_entries[-i - 1] < 0:
                count.append(1)
                ind += 1
            else:
                count.append(0)
                ind += 1
        count.reverse()
        entrydict = []
        for i in zip(self.var_entries, count, range(len(count))):
            diction = {}
            diction["VPD_TPSD"] = self.pid["PID_TPSD"]
            diction["VPD_POS"] = i[2]
            if i[0] >= 0:
                diction["VPD_NAME"] = self.pcf[i[0]]["PCF_NAME"]
                diction["VPD_FIXREP"] = 0
                diction["VPD_DISDESC"] = self.pcf[i[0]]["PCF_DESCR"]
            else:
                diction["VPD_FIXREP"] = pm.evalu(self.entries[-i[0]].array)
                name = (
                    self.pcf[-i[0]]["PCF_NAME"][:3]
                    + str(hash(self.pcf[-i[0]]["PCF_NAME"]))[-5:]
                )
                diction["VPD_NAME"] = name
                diction["VPD_DISDESC"] = "fixed count"
                # I'm not sure how correct this pcf entry is.
                # It has to be here since the "purely informative" fixed-count parameter has to be in pcf.
                diction2 = {}
                diction2["PCF_NAME"] = name
                diction2["PCF_PTC"] = 3
                diction2["PCF_PFC"] = 4
                diction2["PCF_CATEG"] = "N"
                diction2["PCF_NATUR"] = "H"
                diction2["PCF_DESCR"] = diction["VPD_DISDESC"]
                self.pcf.append(diction2)
            diction["VPD_GRPSIZE"] = i[1]
            # diction["VPD_CHOICE"] =
            # diction["VPD_PIDREF"] =
            if i[1] <= 0:
                diction["VPD_WIDTH"] = 0
            else:
                diction["VPD_WIDTH"] = min(
                    int((self.positions[i[0] + 1] - self.positions[i[0]]) / 8), 99
                )
            # diction["VPD_JUSTIFY"] =
            # diction["VPD_NEWLINE"] =
            # diction["VPD_DCHAR"] =
            # diction["VPD_FORM"] =
            # diction["VPD_OFFSET"] =
            entrydict.append(diction)
        return entrydict
