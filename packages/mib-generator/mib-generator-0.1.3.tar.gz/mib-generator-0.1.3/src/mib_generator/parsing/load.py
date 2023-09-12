"""Central location from which other modules can source data from the parsed C-files.

This module is initialised and its methods are called in the first step of the MIB construction process. At this point the C-files
are loaded from the defined paths, are parsed using the :obj:`mib_generator.parsing.parser_main.main` method and are
subsequently available for other scripts throughout the rest of the MIB construction process. The only other
method here is :obj:`extr_values` which serves the purpose creating a global evaluation dictionary holding
values from all header enums, macros, etc...

Attributes:
    TmH (parsing.parser_main.file): Holds the Python parsed representation of the Tm-header C-file.
    TcH (parsing.parser_main.file): Holds the Python parsed representation of the Tc-header C-file.
    TcTmH (parsing.parser_main.file): Holds the Python parsed representation of the TcTm-header C-file.
    TmC (parsing.parser_main.file): Holds the Python parsed representation of the Tm (normal) C-file.
    enumerations (dict): A dictionary containing all possible usable evaluations/enumerations sourced 
        form enums, macros, etc... found in all 3 of the parsed header files.
"""
import os

import json5

import mib_generator.data.warn as warn
import mib_generator.parsing.parser_main as par

TmC_path = ""
TmH_path = ""
TcH_path = ""
TcTmH_path = ""
out_dir = ""
out_doc = ""

TmH = None
TcH = None
TcTmH = None
TmC = None

enumerations = {}

def get_paths():
    """Load paths from the temporary config files.
    
    This method looks up paths to each of the input files in the config files in the runtime config directory. 
    It then saves these paths as global attributes of the :obj:`mib_generator.parsing.load` module, so they can 
    be easily accessed to other methods in the whole program. 
    """
    try:
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "temp", "paths.json5"
        )
        file = open(file_path, "r")
        paths = json5.load(file)
        file.close()
        globals()["TmC_path"] = paths["TmFile"]
        globals()["TmH_path"] = paths["TmHeader"]
        globals()["TcH_path"] = paths["TcHeader"]
        globals()["TcTmH_path"] = paths["TcTmHeader"]
        globals()["out_dir"] = paths["OutDir"]
        globals()["out_doc"] = paths["OutDoc"]
    except:
        warn.raises("EPL1")

def parse_all():
    """Parse the inputted C-files and save the output.
    
    This method uses the :obj:`mib_generator.parsing.parser_main` module to parse contents of the files specified
    at the paths given by global attributes of this module. It then assigns the outputs of the parsing process to
    various other global attributes of this module, so they can be easily accessed.
    """
    try:
        globals()["TmH"] = par.main(TmH_path)
    except:
        warn.raises("EPL2", "Tm .h")
    try:
        globals()["TcH"] = par.main(TcH_path)
    except:
        warn.raises("EPL2", "Tc .h")
    try:
        globals()["TcTmH"] = par.main(TcTmH_path)
    except:
        warn.raises("EPL2", "TcTm .h")
    try:
        globals()["TmC"] = par.main(TmC_path)
    except:
        warn.raises("EPL2", "Tm .c")

def enum_stuff():
    """Create a dictionary that includes all the possible evaluations from the input files.
    
    For each of the inputted (and processed) C-files, this method extracts an evaluation (dictionary
    including all possible variable substitutions, from e.g. `enum` objects.) and then joins all of
    these dictionaries to one and assigns it to a global variable so it can be easily accessed.
    """
    try:
        enum1 = extr_values(TmH)
        enum2 = extr_values(TcTmH)
        enum3 = extr_values(TcH)
        globals()["enumerations"] = enum1 | enum2 | enum3
    except:
        warn.raises("WPL1")

def extr_values(file):
    """Create a dictionary from constants, ``enum`` correspondences, etc... in the given file.

    Goes through all objects in the parsed file and for each ``enum`` and macro, appends the name-value
    pairs present to a dictionary (which represents the "global" evaluation in the file).

    Args:
        file (parsing.parser_main.file): File from which the evaluation dictionary is to be extracted.

    Returns:
        dict: A dictionary with all possible "global" evaluation found in the given file.
    """
    lis = {}
    if file:
        for x in file.structures:
            if x.type == "enum":
                lis.update(x.entries)
            if x.type == "define":
                name = x.name
                if "(" in x.expression:
                    value_raw = x.expression[1:-1]
                else:
                    value_raw = x.expression
                try:
                    value = int(value_raw)
                except:
                    value = None
                if value is not None:
                    lis[name] = value
    return lis
    
def load_all():
    """Run all initialisation and parsing methods.
    
    This method (replacing previous simple initialisation of this module) runs other methods, which 
    
        1. Load the paths to input C-files.
        2. Parse files at these paths.
        3. Create evaluation dictionary from these parsed files.
    """
    get_paths()
    parse_all()
    enum_stuff()
