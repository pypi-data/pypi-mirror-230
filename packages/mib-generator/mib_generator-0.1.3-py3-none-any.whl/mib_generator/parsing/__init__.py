"""These modules serve the purpose of parsing the inputted C/header files into a variety Python
objects, that can be then easily accessed at the later construction stage of the process. The resulting
product with parsed objects should contain all information in the input files, which requires the 
representation to be a bit convoluted from place to place, but still understandable I hope.

The submodules here are:

    * :obj:`load` - Module that allows for interaction between the parser and rest of the code.
    * :obj:`parser_main` - Module that initialises the parsing process for a given file and holds class
      that represents the result.
    * :obj:`par_cfile` - Module that holds the methods and classes for parsing ``.c`` files.
    * :obj:`par_header` - Module that holds the methods and classes for parsing header ``.h`` files.
    * :obj:`par_header` - Module holding various methods that are used by other modules throughout the
      parsing process.
"""
