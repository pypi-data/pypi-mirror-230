"""These modules serve various side roles which are not essential to the functioning of the main generation scipt but make user
interaction with it more straightforward, automatic and pleasant.

The submodules here are:
    
    * :obj:`data_gen` - Module that helped automate inputting all MIB tables parameters into the :obj:`mib_generator.data.longdata` 
      file/method. Unused now.
    * :obj:`update` - Module holding methods that create a small CLI interface (accessible from terminal if the main script
      is run with appropriate flags) that allows the user to update the configuration options and input/output paths.
    * :obj:`visualiser` - Module that provides a GUI representation of the Python objects created by parsing the inputted files.
      Useful mostly for checking the correct functioning of the parser.
"""
