"""This sub-package provides a simple GUI for the MIB Generator.

The GUI is utilised through the Qt6 framework joint with its Python bindings PySide6. The files in this folder/sub-package 
hence follow the format of Qt Creator project. The GUI is however not completely isolated from the rest of the 
:obj:`mib_generator` package and parts of the logic unique to the GUI are also found e.g. in the 
:obj:`mib_generator.data.warn` or :obj:`mib_generator.temp.temp` modules.

The modules/files here are:

    * :obj:`gui` - A module holding the declaration and logic of the GUI as well as its initialisation function.
    * :obj:`gui_methods` - A module holding various side methods utilised by the main GUI.
    * ``form.ui`` - An XML file holding description of all objects in the GUI, their layout, connections, etc.
    * :obj:`ui_form` - A module holding description of the GUI as Python objects. Automatically generated from
      the ``form.ui`` file.
    * ``mib_gui.pyproject`` and ``mib_gui.pyproject.user`` - Files associated with the Qt Creator project which
      makes up the GUI.
"""
