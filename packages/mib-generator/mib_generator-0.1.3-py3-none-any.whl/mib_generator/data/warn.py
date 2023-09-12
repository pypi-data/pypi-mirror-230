"""Takes care of warning and errors that can be raised by the rest of the program.

This module holds both definition of all the errors and warnings that can occur throughout and a method that can be used to 
raise them. (This is made this centralised so that the raising method can be easily changed later if e.g. the UI changes.)

Attributes:
    warnings (dict): A dictionary containing the text definitions of all the possible warnings.
    errors (dict): A dictionary containing the text definitions of all the possible errors.
    complete (dict): A dictionary containing the text definitions of all the possible completion messages.
    display (None or some object): Defines (or holds the object) where the warnings should be raise.
"""

warnings = {
    "WCC1": "Wasn't able to find matching calibration for {} in packet {}.",
    "WCC2": "Wasn't able to find matching decalibration for {} in command {}.",
    "WCC3": "Wasn't able to find the required verification {} for command {}.",
    "WCT1": "Wasn't able to find the common Tc header.",
    "WCT2": "Wasn't able to find the common Tm header.",
    "WCM1": "Wasn't able to find the numerical value of {}.",
    "WCM2": "Wasn't able to establish the link of packet {} to any header structure.",
    "WGM1": "Found repedition in table {}. Deleting rows: {}{}",
    "WGM2": "Tm-packets {} and {} share packet type, subtype and apid, but differ in specification of additional identification field.",
    "WGM3": "Tm-packets {} and {} share packet type, subtype and apid, but do not have additional identification field specified.",
    "WGM4": "The value in table {}, column {}, row {} doesn't have the required type.{}",
    "WGM5": "Missing a mandatory entry in table {}, column {}, row {}.",
    "WGM6": "There are either missing or repeating mnemonics for table {}.{}",
    "WGG1": "Didn't get an input object on basis of which the table {} could be constructed.",
    "WGG2": "The construction of the table {} isn't yet implemented. And hence it wasn't generated.",
    "WMM1": "PySide6 not found. Please install it in order to show the parsed files",
    "WPL1": "Failed to construct the list of available enumerations.",
    "WPM1": "Invalid logic encountered when parsing preprocessor directives.",
    "WTT1": "The path {} for file {} does not exist, consider using previous value {}.",
    "WTT2": "The path {} for file {} does not exist (and there is no valid previous value to use in its place).",
    "WGU1": "The directory {} to which the config files are to be saved doesn't exist."
}

errors = {
    "EPL1": "Failed to load (some of) the input/output paths.",
    "EPL2": "Failed to load the {} C file.",
    "EPM1": "Failed loading json5 comment: {}",
    "EGU1": "Failed filling in the default config directory path.",
    "EGU2": "Failed saving the specified paths to runtime config file.",
    "EGU3": "Failed saving the configuration parameters above to runtime config file.",
    "EGU4": "Failed loading configuration (+paths) from config files in the specified directory.",
    "EGU5": "Failed saving the current configuration (+paths) to config files in the specified directory.",
    "EGU6": "Failed running the parsing process.",
    "EGU7": "Failed compiling TM packets characteristics from parsed files.",
    "EGU8": "Failed compiling TC packets characteristics from parsed files.",
    "EGU9": "Failed constructing the specified MIB tables.",
    "EGUA": "Failed constructing the .docx file.",
    "EGUB": "Failed saving the constructed MIB tables.",
    "EGUC": "Failed saving the constructed .docx file.",
    "EGUD": "Failed opening the visualisation of {} file.",
}

complete = {
    "CGU1": "Filled in the default config directory path.",
    "CGU2": "Saved the specified paths to runtime config file.",
    "CGU3": "Saved the configuration parameters above to runtime config file.",
    "CGU4": "Loaded configuration (+paths) from config files in the specified directory.",
    "CGU5": "Saved the current configuration (+paths) to config files in the specified directory.",
    "CGU6": "Ran the parsing process.",
    "CGU7": "Finished compiling TM packets characteristics from parsed files.",
    "CGU8": "Finished compiling TC packets characteristics from parsed files.",
    "CGU9": "Finished constructing the specified MIB tables.",
    "CGUA": "Finished constructing the .docx file.",
    "CGUB": "Saved the constructed MIB tables.",
    "CGUC": "Saved the constructed .docx file.",
}

display = None

def disp_update(var):
    """Update the :attr:`display` global variable in this module to the specified value.
    
    This quite ugly method (or approach) serves the purpose of specifying to the method that takes care of raising warnings, that
    the warnings shouldn't be printed to terminal but rather added to the object's text (the passed object is expected to be some GUI console).
    
    Args:
        var (object such as PySide6.QtWidgets.QTextEdit): The object to be assigned to the :attr:`display` global variable.
    """
    globals()["display"] = var

def raises(ID, *data):
    """Raise warning/error with the given ID.

    This method looks up a warning/error text for a given passed ID, formats it with other passed parameters and
    then displays it - either to terminal if the global attribute :attr:`display` is ``None`` or to the object that this attribute holds..

    Args:
        ID (str): The ID identifying the warning/error of format 3 capital letters + one-digit number.
        \*data (\*args): Additional parameters which are to be formatted into the warning/error text.
    """
    if ID[:1] in {"w", "W"}:
        if ID in warnings.keys():
            stri = "Warn.:\t" + warnings[ID].format(*data)
        else:
            stri = "Warn.:\tUnspecified warning with ID {} encountered.".format(ID)
    elif ID[:1] in {"e", "E"}:
        if ID in errors.keys():
            stri = "Error:\t" + errors[ID].format(*data)
        else:
            stri = "Error:\tUnspecified error with ID {} encountered.".format(ID)
    elif ID[:1] in {"c", "C"}:
        if ID in complete.keys():
            stri = "Compl.:\t" + complete[ID].format(*data)
        else:
            stri = "Compl.:\tUnspecified completion message with ID {} encountered.".format(ID)
    else:
        stri = "Warn.:\tWarning/Error/Completion message with unknown ID {} encountered.".format(ID)
    if not display:
        print(stri)
    else:
        display.append(stri)
