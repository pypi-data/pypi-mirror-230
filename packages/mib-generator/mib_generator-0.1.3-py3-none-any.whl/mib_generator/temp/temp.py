"""This module holds method/s which take care of transferring the config files between directories and getting their data.

At runtime, the whole program works with config files which are stored in the :obj:`mib_generator.temp` sub-package/file, which
means that before all of the generation processes happen, the config files from the default directory (:obj:`mib_generator.data`)  
have to be moved there, which is one of the jobs of this module, the others being the same inversed, loading of config data, etc.
"""
import os
import shutil

import json5

import mib_generator.data.warn as warn


def move_conf(dire=None):
    """Transfer the config files from the specified directory to runtime location.

    This method looks at the passed directory, checks what config files are inside it and if such are found, moves them
    to the package runtime directory (:obj:`mib_generator.temp`), rewriting config files which might have been there already.
    If some config file is not found in the specified directory, transfers config from the default directory
    (:obj:`mib_generator.data`) instead.

    Args:
        dire (str): A string specifying the directory from which the config files are to be taken.
    """
    here = os.path.dirname(__file__)
    data = os.path.join(os.path.dirname(here), "data")
    if dire and os.path.isfile(os.path.join(dire, "paths.json5")):
        source_p = os.path.join(dire, "paths.json5")
    else:
        source_p = os.path.join(data, "paths.json5")
    shutil.copy(source_p, here)
    if dire and os.path.isfile(os.path.join(dire, "config.json5")):
        source_c = os.path.join(dire, "config.json5")
    else:
        source_c = os.path.join(data, "config.json5")
    shutil.copy(source_c, here)
    
def evom_conf(dire):
    """Cope the runtime config files to the specified directory.
    
    This module is passed a directory location, it check whether it exists and if yes, copies the current
    runtime config files to there.
    
    Args:
        dire (str): A path to directory where the config files are to be copied.
    """
    here = os.path.dirname(__file__)
    temp = os.path.join(os.path.dirname(here), "temp")
    if os.path.isdir(dire):
        shutil.copy(os.path.join(temp, "config.json5"),os.path.join(dire, "config.json5"))
        shutil.copy(os.path.join(temp, "paths.json5"),os.path.join(dire, "paths.json5"))
    
def update_paths(diction):
    """Update paths in the ``"paths.json5"`` config file to the passed values.
    
    Goes through each entry in the passed dictionary and if it recognises it as valid configuration path,
    it saves it to the runtime config file. If it is given a path to file which doesn't exists, it raises
    a warning but saves it nonetheless.
    
    Args:
        diction (dict): A dictionary containing paths to the input/output files/directories.
        
    Returns:
        dict: A dictionary of the values saved. (currently the same as the inputted dictionary)
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "paths.json5"
    )
    try:
        fil = open(file_path, "r")
        leg_data = json5.load(fil)
        fil.close()
    except:
        leg_data = {}
    for i in diction:
        if os.path.isfile(diction[i]) or os.path.isdir(diction[i]):
            pass
        else:
            if i in leg_data.keys():
                F = os.path.isfile(leg_data[i])
                D = os.path.isdir(leg_data[i])
                if F or D:
                    warn.raises("WTT1",diction[i], i, leg_data[i])
                else:
                    warn.raises("WTT2", diction[i], i)
            else:
                warn.raises("WTT2", diction[i], i)
    
    fil = open(file_path, "w")
    fil.write("// This file stores various paths to source/output files\n")
    fil.write(json5.dumps(diction))
    fil.close()
    return diction
    
def fetch_paths():
    """Get paths dictionary from the runtime config file.
    
    Loads the paths config file in the runtime directory (the :obj:`mib_generator.temp` sub-package) and
    extracts the paths to input/output files from it as a dictionary.
    
    Returns:
        dict: A dictionary containing the paths to input/output files/directories.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "paths.json5"
    )
    try:
        fil = open(file_path, "r")
        leg_data = json5.load(fil)
        fil.close()
    except:
        leg_data = {}
    return leg_data
            
