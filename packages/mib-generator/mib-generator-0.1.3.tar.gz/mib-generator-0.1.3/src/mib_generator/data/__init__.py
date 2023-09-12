"""The files and submodules in this package/folder serve as a storage of data and global-level
variables which are mostly stored here in order not to cluster the code somewhere else and in order
to be easily accessible by any other file.

The files/submodules here are:

    * :obj:`longdata` - This giant module stores mostly all information about the structures of MIB
      tables and what checks should be performed by each entry in them.
    * :obj:`warn` - Module storing definition of various warnings and errors that can be raised by the program. 
    * ``paths.json5`` - This file stores default information about paths to the input/output files in a json5 format.
    * ``config.json5`` - This file stores default config information which mostly include what pre-processor macros
      should be taken as defined when parsing the inputted files and what mib tables should be generated.
"""
