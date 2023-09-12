"""Sub-package taking care of runtime configuration.

This sub-package/folder serves the role of a location where config files are stored at the runtime and from where all other parts
of the program ask for them. It also holds module which takes care of transfer of these files.

The files/sub-modules here are:

    * :obj:`temp` - Module holding methods which manipulate the config files and transfer them here if needed.
    * ``paths.json5`` - This file stores runtime information about paths to the input/output files in a json5 format.
    * ``config.json5`` - This file stores runtime config information which mostly include what pre-processor macros
      should be taken as defined when parsing the inputted files and what mib tables should be generated.
"""
