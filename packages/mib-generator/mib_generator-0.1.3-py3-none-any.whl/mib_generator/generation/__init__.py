"""This sub-package and the modules within it serve the purpose of turning previously interpreted and comprehended
representations of Tc/Tm packets/etc. and their sketched out MIB tables into propertly constructed and verified (against
criteria of type, uniqueness, etc...) MIB tables and finally saving these tables in the correct format into a desired
location and documenting the output.

The submodules here are:
    * :obj:`gener` - The main generation module, chooses what should be generated, what tools should be used for that
      purpose and executes the generation.
    * :obj:`gener_methods` - Module holding methods used by the main generation module. These methods do all from checking
      and converting MIB tables to saving them in the correct location.
    * :obj:`gener_doc` - Module with methods that create a docx file with the list of entries in Tm and Tc packets from
      which the MIB tables were generated.
"""
