"""The main parsing module.

This module is a starting point for parsing of C-files and holds class which plays the role of their interpretation.
"""

import mib_generator.parsing.par_cfile as parc
import mib_generator.parsing.par_header as parh
import mib_generator.parsing.par_methods as parm


class file:
    """Class representing the file being analysed and its internal structure in an easily Python-accessible format.

    During creation this class goes through multiple steps of parsing/interpretation using methods
    in :obj:`mib_generator.parsing.par_header`, :obj:`mib_generator.parsing.par_cfile`
    and :obj:`parsing.par_methods`. The steps are as follows:

    1. Get general information about the file (length, line indexes)
    2. Separate text in comment and the code (while keeping the absolute positions in the file).
    3. Process any C-preprocessor logic that's in the code.
    4. Parse the resulting code into Python representations of the corresponding C-objects.
    5. Parse the comments into intepretable sections (written in json5) and interpret their content.
    6. Create links between the found C-objects and interterpretable comments

    Args:
        stri (str): The content of the file to be parsed/analysed.
        header (bool): Parameter denoting whether file is a header or normal C file.

    Attributes:
        text (str): Text of the file.
        max_position (int): Length of the file.
        lines (list): List of positions of line starts.
        text_o (str): File text with only code (without comments).
        text_c (str): File text with only comments (without code).
        text_f (str): File (with code) after sorting out the pre-processor logic.
        structures (list): List of Python representations of C-objects found in the file.

            The Python representations are child classes of either :obj:`mib_generator.parsing.par_cfile.instance_og`
            or :obj:`mib_generator.parsing.par_header.structure`
        comments (list): List of found interpretable comments which are represented using
            :obj:`mib_generator.parsing.par_methods.comment`
        link (list): List of pairs of comments and the Python representation of C-objects they belong to.
    """

    def __init__(self, stri, header):
        self.text = stri
        self.max_position = len(stri)
        self.lines = parm.line_index(stri)
        self.text_o, self.text_c = parm.split_comment(stri)
        self.text_f = parm.preproc_filter(self.text_o)
        if header:
            self.structures = parh.str_parse(self.text_f)
        else:
            self.structures = parc.str_parse(self.text_f)
        self.comments = parm.com_parse(self.text_c)
        self.link = self.linker()

    def linker(self):
        """Link each comment to a corresponding C-object in the file

        Goes one by one through comments and searches for their corresponding structure.
        For the closes found match, creates link from the comment to the structure and from the structure to the comment
        (by generating attributes for their respectives classes) and returns them in a list of pairs.

        Returns:
            list of pairs: Pairs of comments and their corresponding structures.
        """
        pairs = []
        for i in self.comments:
            ind = i.start
            elem = {}
            minim = 50000
            for l in self.structures:
                if l.start <= ind <= l.end:
                    if l.type != "enum":  # very ugly bodge again
                        for k in l.elements:
                            if ind - k.start >= 0 and ind - k.start <= minim:
                                elem = k
                                minim = ind - k.start
                    else:
                        elem = l
                        minim = 49999

                    break
            if minim == 50000:
                for l in self.structures:
                    if l.start - ind >= 0 and l.start - ind <= minim:
                        elem = l
                        minim = l.start - ind
            pairs.append([i, elem])
            elem.comment.append(i)
            i.structure = elem
        return pairs


def main(name="/home/vachaj11/Documents/MIB/start/src/PUS_TmDefs.h"):
    """Create a parsed python representation of a file.

    Opens file, depending on its ending chooses correct parser and lets it run.

    Args:
        name (str): Path to file.

    Returns:
        file: File object
    """

    try:
        fil = open(name, "r")
        c = fil.read()
        fil.close()
    except:
        c = ""
    if name[-1] == "h":
        x = file(c, True)
    else:
        x = file(c, False)
    x.path = name
    return x
