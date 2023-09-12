"""Methods and classes for construction, representation and calibrating of calibrations/decalibrations/verifications.

This module puts together all classes and function that represent the calibration and verification parts of MIB databases.
These representations only collect all information about the structure of the calibrations and its corresponding MIB tables
in a structured form (but are not functional themselves).
"""
import mib_generator.data.warn as warn
import mib_generator.parsing.load as load


def cur_update(packet, cal):
    """Check whether calibration exists for parameters which require it and if yes, change cur entries correspondingly.

    For a given TM packet goes through all of its entries/parameters and for each checks whether its corresponding calibration
    (if stated) exists. If yes, then it updates the name of the calibration in the packet to its correct referential value.

    Initially this method did this for both cases of single and multiple calibration associated to a parameter. However later
    I focused only on the single case (the ``"PCF_CURTX"`` entry of the parameter) so the other case (the entries in ``cur``
    table associated to the parameter) might not work anymore.

    Args:
        packet (TM_packet.TM_packet): Packet, who's entries' calibrations are to be checked and updated.
        cal (dict): A dictionary holding lists of various types of calibration. Each is a child-class of :obj:`calib`.
    """
    calibs = []
    for i in cal:
        for l in cal[i]:
            calibs.append(l)
    for i in packet.cur:
        match_count = 0
        for l in calibs:
            if i["CUR_SELECT"] == l.name:
                i["CUR_SELECT"] = l.comment.entries["cal_ident"]
                match_count += 1
        if match_count == 0:
            warn.raises("WCC1", i["CUR_PNAME"], str(packet.pid["PID_SPID"]))
            packet.cur.remove(i)
    for i in packet.pcf:
        if "PCF_CURTX" in i.keys() and i["PCF_CURTX"]:
            match_count = 0
            for l in calibs:
                if i["PCF_CURTX"] == l.name:
                    i["PCF_CURTX"] = l.comment.entries["cal_ident"]
                    match_count += 1
                    if "txf" in l.__dir__():
                        i["PCF_CATEG"] = "S"
            if match_count == 0:
                warn.raises("WCC1", i["PCF_CURTX"], str(packet.pid["PID_SPID"]))
                i["PCF_CURTX"] = ""


def cpc_update(command, dec):
    """Check whether decalibration exists for parameter which require it and if yes, change cpc entry correspondingly.

    For a given TC command, goes through all of its parameters and for each checks whether its corresponding decalibration
    (if declared) exists. If yes, then it updates the name of the decalibration in the command parameter to its correct
    referential value.

    Args:
        command (TC_packet.TC_packet): Command, who's parameters' decalibrations are to be checked and updated.
        dec (list): List of all available decalibrations. Each of type :obj:`decalib`.
    """
    for i in command.cpc:
        if "CPC_PAFREF" in i.keys() and i["CPC_PAFREF"]:
            match_count = 0
            for l in dec:
                if i["CPC_PAFREF"] == l.name:
                    i["CPC_PAFREF"] = l.comment.entries["dec_ident"]
                    match_count += 1
            if match_count == 0:
                warn.raises("WCC2", i["CPC_PAFREF"], str(command.ccf["CCF_CNAME"]))
                i["CPC_PAFREF"] = ""


def calib_extract(comments):
    """Extract declaration of various calibrations if they occur in the comments.

    This function goes through inputted list of interpreted comments and looks (based on the entries in them) for ones which
    hold definition of calibrations. Based on such definition it first decides what calibrations these are and subsequently
    interprets them through appropriate calibration classes. From all of such interpreted calibration it then creates a
    dictionary where they are joined in lists by their types.

    Args:
        comments (list): List of interpreted comments. Each of type :obj:`mib_generator.parsing.par_methods.comment`.

    Returns:
        dict: A dictionary holding lists of interpreted calibrations sorted by their types. Each calibration is of some
            child-class of :obj:`calib`.
    """
    mcfs = []
    txfs = []
    cafs = []
    lgfs = []
    for i in comments:
        keys = i.entries.keys()
        if "cal_ident" in keys:
            if "mcf" in keys:
                mcfs.append(mcf_calib(i))
            elif bool({"text_cal", "enum"} & keys):
                txfs.append(txf_calib(i))
            elif "lgf" in keys:
                lgfs.append(lgf_calib(i))
            elif "num_cal" in keys:
                cafs.append(caf_calib(i))
    return {"mcfs": mcfs, "txfs": txfs, "cafs": cafs, "lgfs": lgfs}


def decal_extract(comments):
    """Extract declarations of decalibrations from comments.

    This function goes through inputted list of interpreted comments and looks (based on the entries in them) for ones which
    hold definition of decalibrations. It then interprets these with an appropriate class (:obj:`decalib`) and construct a
    list of them.

    Args:
        comments (list): List of interpreted comments. Each of type :obj:`mib_generator.parsing.par_methods.comment`.

    Returns:
        list: A list of all found decalibrations. Each of the type :obj:`decalib`.
    """
    decal = []
    for i in comments:
        if "dec_ident" in i.entries.keys():
            decal.append(decalib(i))
    return decal


class calib:
    """General class of calibrations/decalibrations.

    This class is a parent class of all the various types of interpreted calibrations/decalibrations. It hence holds only very
    general attributes that all of them require. It is created based on intepreted comment passed at creation.

    Args:
        comment (parsing.par_methods.comment): A comment from which the calibration is to be created.

    Attributes:
        comment (parsing.par_methods.comment): The comment from which this calibration was created.
        name (str): The name of the calibration (that is, its internal name, not the identifier name passed into the MIB table).
    """

    def __init__(self, comment):
        self.comment = comment
        if "cal_def" in comment.entries.keys():
            self.name = comment.entries["cal_def"]
        else:
            self.name = comment.entries["enum"]


class mcf_calib(calib):
    """Class of a polynomial mcf calibration.

    This class represents a polynomial calibration and its corresponding mcf table. It is created from an interpreted comment
    and is a child-class of :obj:`calib` who's initialisation **arguments** and **attributes** it shares.

    Attributes:
        mcf (dict): Dictionary corresponding to one line in MIB mcf table.
    """

    def __init__(self, comment):
        calib.__init__(self, comment)
        self.mcf = self.mcf_dictionary()

    def mcf_dictionary(self):
        """Define elements for entry in mcf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the mcf table (with the
        key being the name of the column and value the entry to be filled in). Here the values are extracted from the values in
        the starting comment with the polynomial coefficients being extracted in the ``for...`` loop.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`mcf`.
        """
        diction = {}
        diction["MCF_IDENT"] = self.comment.entries["cal_ident"]
        diction["MCF_DESCR"] = self.comment.entries["desc"]
        for i in range(5):
            try:
                diction["MCF_POL" + str(i + 1)] = self.comment.entries["mcf"][
                    "a" + str(i)
                ]
            except:
                diction["MCF_POL" + str(i + 1)] = ""
        return diction


class lgf_calib(calib):
    """Class of a logarithmic lgf calibration.

    This class represents a logarithmic calibration and its corresponding lgf table. It is created from an interpreted comment
    and is a child-class of :obj:`calib` who's initialisation **arguments** and **attributes** it shares.

    Attributes:
        lgf (dict): Dictionary corresponding to one line in MIB lgf table.
    """

    def __init__(self, comment):
        calib.__init__(self, comment)
        self.lgf = self.lgf_dictionary()

    def lgf_dictionary(self):
        """Define elements for entry in lgf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the lgf table (with the
        key being the name of the column and value the entry to be filled in). Here the values are extracted from the values in
        the starting comment with the logarithmic coefficients being extracted in the ``for...`` loop.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`lgf`.
        """
        diction = {}
        diction["LGF_IDENT"] = self.comment.entries["cal_ident"]
        diction["LGF_DESCR"] = self.comment.entries["desc"]
        for i in range(5):
            try:
                diction["LGF_POL" + str(i + 1)] = self.comment.entries["lgf"][
                    "a" + str(i)
                ]
            except:
                diction["LGF_POL" + str(i + 1)] = ""
        return diction


class txf_calib(calib):
    """Class of a textual calibration.

    This class represents a textual calibration and its corresponding txf and txp tables. It is created from an interpreted
    comment and is a child-class of :obj:`calib` who's initialisation **arguments** and **attributes** it shares.

    The unusual thing here is that textual calibration can be declared in the starting C-files in two ways - either wholly in
    the text of a comment or through a combination of an ``enum`` and comments. Because of that the creation of representation
    here is maybe a bit convoluted.

    Attributes:
        enum (bool): ``True`` if the calibration is defined through an ``enum`` and ``False`` if wholly in one comment.
        type (str): Type of the data this calibration is used on. Corresponding to the ``"TXF_RAWFMT"`` MIB entry.
        length (str): Number of entries (in integer) that this calibration should be defined by.
        txf (dict): Dictionary corresponding to one line in MIB txf table.
        txp (list): List of dictionaries each one corresponding to one line in MIB txp table.
    """

    def __init__(self, comment):
        calib.__init__(self, comment)
        self.enum = self.is_enum()
        self.type, self.length = self.txf_data()
        self.txf = self.txf_dictionary()
        self.txp = self.txp_listdict()

    def is_enum(self):
        """Check whether the calibration is saved in the header file as enum.

        Based on the content of the initialisation content, checks whether this calibration is defined through ``enum`` or not.

        Returns:
            bool: ``True`` if it is defined through an ``enum``, ``False`` if it is defined wholly in a comment.
        """
        if "enum" in self.comment.entries.keys():
            return True
        else:
            return False

    def txf_data(self):
        """Get information about the nature of data calibrated.

        From the entries either in an ``enum`` or in the comment, extracts information about the nature of the data to be
        calibrated and the length of the textual calibration (number of its entries).

        Returns:
            tuple: A tuple consisting of:

                * *str* - The type of the data for calibration. See :attr:`type`.
                * *str* - The number of entries in this calibration. See :attr:`length`.
        """
        try:
            if not self.enum:
                minim = self.comment.entries["text_cal"]["min"]
                leng = str(len(self.comment.entries["text_cal"]["lookup"]))
            else:
                minim = min(self.comment.structure.entries.values())
                leng = str(len(self.comment.structure.entries))
            if type(minim) is not int:
                flav = "R"
            elif minim < 0:
                flav = "I"
            else:
                flav = "U"
        except:
            flav = ""
            leng = ""
        return flav, leng

    def txf_dictionary(self):
        """Define elements for entry in txf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the txf table (with the
        key being the name of the column and value the entry to be filled in). Here the MIB table entries are mostly
        straightforwardly assigned already identified values.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`txf`.
        """
        diction = {}
        diction["TXF_NUMBR"] = self.comment.entries["cal_ident"]
        try:
            diction["TXF_DESCR"] = self.comment.entries["desc"]
        except:
            diction["TXF_DESCR"] = ""
        diction["TXF_RAWFMT"] = self.type
        diction["TXF_NALIAS"] = self.length
        return diction

    def txp_listdict(self):
        """Define elements for entries in txp table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the txp table
        (with the key being the name of the column and value the entry to be filled in). Here the process is again complicated
        by the fact that the there are two ways in which textual calibration can be defined. In case of ``enum`` it has to be
        further "guessed" what text-values correspond to which numerical value, which might not be entirely reliable (it is
        done like this because the Python representation of ``enum`` that I created does not define the ``enum`` entries
        as individual objects).

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`txp`.
        """
        entrydict = []
        if not self.enum:
            for i in self.comment.entries["text_cal"]["lookup"]:
                diction = {}
                diction["TXP_NUMBR"] = self.txf["TXF_NUMBR"]
                try:
                    if "val" in i.keys():
                        diction["TXP_FROM"] = i["val"]
                        diction["TXP_TO"] = i["val"]
                    else:
                        diction["TXP_FROM"] = i["from"]
                        diction["TXP_TO"] = i["to"]
                    diction["TXP_ALTXT"] = i["text"]
                except:
                    diction["TXP_FROM"] = ""
                    diction["TXP_TO"] = ""
                    diction["TXP_ALTXT"] = ""
                entrydict.append(diction)
        else:
            entries = list(self.comment.structure.entries.items())
            for i in range(len(entries)):
                diction = {}
                diction["TXP_NUMBR"] = self.txf["TXF_NUMBR"]
                diction["TXP_FROM"] = entries[i][1]
                diction["TXP_TO"] = entries[i][1]
                try:
                    diction["TXP_ALTXT"] = self.comment.structure.comment[
                        -self.length + i
                    ].entries["text"]
                except:
                    diction["TXP_ALTXT"] = "-1"
                entrydict.append(diction)
        return entrydict


class caf_calib(calib):
    """Class of a numerical calibration.

    This class represents a numerical calibration and its corresponding caf and cap tables. It is created from an interpreted
    comment and is a child-class of :obj:`calib` who's initialisation **arguments** and **attributes** it shares.

    It hasn't been fully decided yet what the syntax for declaring these calibrations should be, so some of the
    extraction/construction steps here might not be entirely correct. As of now it is assumed that numerical calibration
    definition would look analogously to textual calibration (the non-``enum`` one).

    Attributes:
        type (list): Type of the data (defined through two strings, hence the list) this calibration is used on.
            Corresponding to the ``"CAF_RAWFMT"`` and ``"CAF_ENGFMT"`` MIB entries.
        length (str): Number of entries (in integer) that this calibration should be defined by.
        caf (dict): Dictionary corresponding to one line in MIB caf table.
        cap (list): List of dictionaries each one corresponding to one line in MIB cap table.
    """

    def __init__(self, comment):
        calib.__init__(self, comment)
        self.type, self.length = self.caf_data()
        self.caf = self.caf_dictionary()
        self.cap = self.cap_listdict()

    def caf_data(self):
        """Get information about the nature of data calibrated.

        From the entries in the comment, extracts information about the nature of the data to be calibrated and the length of
        the numerical calibration (number of its entries).

        Returns:
            tuple: A tuple consisting of:

                * *list* - The type of the data for calibration. See :attr:`type`.
                * *str* - The number of entries in this calibration. See :attr:`length`.
        """
        try:
            entries = self.comment.entries["num_cal"]
            raw = []
            eng = []
            for i in entries:
                raw.append(i[0])
                eng.append(i[1])
            if type(sum(raw)) is not int:
                flav_r = "R"
            elif min(raw) < 0:
                flav_r = "I"
            else:
                flav_r = "U"
            if type(sum(eng)) is not int:
                flav_e = "R"
            elif min(eng) < 0:
                flav_e = "I"
            else:
                flav_e = "U"
            leng = str(len(self.comment.entries["num_cal"]))
        except:
            flav_r = ""
            flav_e = ""
            leng = ""
        return [flav_r, flav_e], leng

    def caf_dictionary(self):
        """Define elements for entry in caf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the caf table (with the
        key being the name of the column and value the entry to be filled in). Here the MIB table entries are mostly
        straightforwardly assigned already identified values.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`caf`.
        """
        diction = {}
        diction["CAF_NUMBR"] = self.comment.entries["cal_ident"]
        diction["CAF_DESCR"] = self.comment.entries["desc"]
        diction["CAF_ENGFMT"] = self.type[1]
        diction["CAF_RAWFMT"] = self.type[0]
        # diction["CAF_RADIX"] =
        # diction["CAF_UNIT"] =
        diction["CAF_NCURVE"] = self.length
        # diction["CAF_INTER"] =
        return diction

    def cap_listdict(self):
        """Define elements for entries in cap table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the cap table
        (with the key being the name of the column and value the entry to be filled in). The construction here assumes the
        X-Y data being stored in list of ``[X,Y]`` pairs under the key ``"num_cal"`` in the comment declaring this calibration.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`cap`.
        """
        entrydict = []
        for i in self.comment.entries["num_cal"]:
            diction = {}
            diction["CAP_NUMBR"] = self.caf["CAF_NUMBR"]
            diction["CAP_XVALS"] = i[0]
            diction["CAP_YVALS"] = i[1]
            entrydict.append(diction)
        return entrydict


class decalib(calib):
    """Class of a textual decalibration for TC commands.

    This class represents a textual decalibration used for TC commands and its corresponding paf and pas tables. It is created
    from an interpreted comment and is a child-class of :obj:`calib` who's initialisation **arguments** and **attributes** it
    shares.

    Attributes:
        type (str): Type of the data this decalibration is used on. Corresponding to the ``"PAF_RAWFMT"`` MIB entry.
        length (str): Number of entries (in integer) that this calibration should be defined by.
        paf (dict): Dictionary corresponding to one line in MIB paf table.
        pas (list): List of dictionaries each one corresponding to one line in MIB pas table.
    """

    def __init__(self, comment):
        calib.__init__(self, comment)
        self.type, self.length = self.paf_data()
        self.paf = self.paf_dictionary()
        self.pas = self.pas_listdict()

    def paf_data(self):
        """Get information about the nature of data calibrated.

        From the entries in the comment, extracts information about the nature of the data to be de/calibrated and the
        length of the textual decalibration (number of its entries).

        Returns:
            tuple: A tuple consisting of:

                * *str* - The type of the data for calibration. See :attr:`type`.
                * *str* - The number of entries in this calibration. See :attr:`length`.
        """
        try:
            minim = min(self.comment.structure.entries.values())
            leng = len(self.comment.structure.entries)
            if type(minim) is not int:
                flav = "R"
            elif minim < 0:
                flav = "I"
            else:
                flav = "U"
        except:
            flav = ""
            leng = ""
        return flav, leng

    def paf_dictionary(self):
        """Define elements for entry in paf table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the paf table (with the
        key being the name of the column and value the entry to be filled in). Here the MIB table entries are mostly
        straightforwardly assigned already identified values.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`paf`.
        """

        diction = {}
        diction["PAF_NUMBR"] = self.comment.entries["dec_ident"]
        try:
            diction["PAF_DESCR"] = self.comment.entries["desc"]
        except:
            diction["PAF_DESCR"] = ""
        diction["PAF_RAWFMT"] = self.type
        diction["PAF_NALIAS"] = self.length
        return diction

    def pas_listdict(self):
        """Define elements for entries in pas table.

        Creates a list of dictionaries in each of which a key-value pair corresponds to entry in one column of the pas table
        (with the key being the name of the column and value the entry to be filled in). Here, since the Python description of
        ``enum`` in this code does not support comment associated to its specific entry, it has to be in a way "guessed" what
        this correspondence is, which is something to keep an eye on.

        Returns:
            list: List of dictionaries which are to be lines in the MIB table. Assigned to :attr:`pas`.
        """
        entrydict = []
        entries = list(self.comment.structure.entries.items())
        for i in range(len(entries)):
            diction = {}
            diction["PAS_NUMBR"] = self.paf["PAF_NUMBR"]
            diction["PAS_ALVAL"] = entries[i][1]
            try:
                diction["PAS_ALTXT"] = self.comment.structure.comment[
                    -self.length + i
                ].entries["text"]
            except:
                diction["PAS_ALTXT"] = "-1"
            entrydict.append(diction)
        return entrydict


def verif_extract(comments):
    """Extract declarations of verifications from comments.

    This function goes through inputted list of interpreted comments and looks (based on the entries in them) for ones which
    hold definition of verifications. It then interprets these with an appropriate class (:obj:`verification`) and construct a
    list of them.

    Args:
        comments (list): List of interpreted comments. Each of type :obj:`mib_generator.parsing.par_methods.comment`.

    Returns:
        list: A list of all found verifications. Each of the type :obj:`verification`.
    """
    verif = []
    for i in comments:
        if "cvs_def" in i.entries.keys():
            verif.append(verification(i))
    return verif


def cvs_update(command, verifs):
    """Check whether verification exists for a given command and if yes, change cvs entry correspondingly.

    For a given TC command checks whether its corresponding verification (if declared) exists. If yes, then it updates the
    name of the verification in the command parameter to its correct referential value, otherwise warning is raised.
    If no verifications were declared for this command (excluding the case where explicitely no verification were declared,
    i.e. ``[]`` was given as the list of verifications), then default selection of verifications is used and corresponding
    entries in cvp and cvs tables are created.

    Args:
        command (TC_packet.TC_packet): Command, who's verification entries are to be checked and updated.
        verifs (list): List of all available verifications. Each of type :obj:`verification`.
    """
    if command.cvp is None:
        entrydict = []
        for i in verifs:
            if i.default:
                diction = {}
                diction["CVP_TASK"] = command.ccf["CCF_CNAME"]
                diction["CVP_TYPE"] = "C"
                diction["CVP_CVSID"] = i.cvs["CVS_ID"]
                entrydict.append(diction)
        command.cvp = entrydict
    else:
        lis = []
        for i in verifs:
            lis.append(i.cvs["CVS_ID"])
        maxi = len(command.cvp)
        for i in range(maxi):
            if command.cvp[maxi - 1 - i]["CVP_CVSID"] not in lis:
                warn.raises(
                    "WCC3",
                    str(command.cvp[maxi - 1 - i]["CVP_CVSID"]),
                    str(command.ccf["CCF_CNAME"]),
                )
                command.cvp.pop(maxi - i - 1)


class verification:
    """Class of a TC command verification.

    This class represents a verification of a TC command and its corresponding cvs table. It is created from an interpreted
    comment. It is further also identified whether the verification should be applied as a default or not, which is later used
    when checking/correcting verifications declared for specific commands.

    Attributes:
        comment (parsing.par_methods.comment): The comment from which this verification was created.
        default (bool): ``True`` if this verification is to be applied as default, ``False`` otherwise.
        cvs (dict): Dictionary corresponding to one line in MIB cvs table.
    """

    def __init__(self, comment):
        self.comment = comment
        self.default = self.is_default()
        self.cvs = self.cvs_dictionary()

    def is_default(self):
        """Decide whether this verification should be applied as a default.

        Checks the verification declaration for an information on whether it should be applied as a default or not. If no such
        information is found, returns that it shouldn't, otherwise returns the information (as a boolean).

        Returns:
            bool: ``True`` if this verification is to be applied as default, otherwise ``False``.
        """
        if "default" in self.comment.entries.keys():
            return bool(self.comment.entries["default"])
        else:
            return False

    def cvs_dictionary(self):
        """Define elements for entry in cvs table.

        Creates a dictionary where each key-value pair corresponds to an entry in one column of the cvs table (with the
        key being the name of the column and value the entry to be filled in). Here values from the initialisation comment
        are straightforwardly assigned.

        Returns:
            dict: Dictionary which is one line in the MIB table. Assigned to :attr:`cvs`.
        """
        diction = {}
        diction["CVS_ID"] = self.comment.entries["cvs_def"]
        try:
            diction["CVS_TYPE"] = self.comment.entries["cvs_type"]
        except:
            diction["CVS_TYPE"] = ""
        if "cve" in self.comment.entries.keys():
            diction["CVS_SOURCE"] = "V"
        else:
            diction["CVS_SOURCE"] = "R"
        try:
            diction["CVS_START"] = self.comment.entries["cvs_start"]
        except:
            diction["CVS_START"] = 0
        try:
            diction["CVS_INTERVAL"] = self.comment.entries["cvs_interval"]
        except:
            diction["CVS_INTERVAL"] = ""
        # diction["CVS_SPID"] = ""
        # diction["CVS_UNCERTAINTY"] = ""
        return diction
