"""The modules here serve the purpose of constructing all the various types of MIB tables. They generally
take the Python representation of the C-files generated as the result of the parsing process, and by looking
what objects are included, in what order, of what types, with what comments, etc... They generate the appropriate
entries in MIB tables for them. For conciseness sake, these entries are here generated as dictionaries which are attributes of some 
constructed object - TM packet (:obj:`TM_packet.TM_packet`), TC packet (:obj:`TC_packet.TC_packet`), calibration/decalibration 
(:obj:`calib.calib`), verification (:obj:`calib.verification`), etc... - which are in a sense abstract representation of the
underlying logical structure of the packets/communication standards.

The submodules here are:

    * :obj:`TM_packet` - Module that holds classes that represent the TM header and each TM packet including all the MIB tables 
      that are connected to each of them.
    * :obj:`TM_packet_methods` - Module that holds various methods that are used when constructing the MIB tables which are
      attributes of the :obj:`TM_packet.TM_packet` class.
    * :obj:`TC_packet` - Module that holds classes that represent the TC header and each TC packet including all the MIB tables 
      that are connected to each of them.
    * :obj:`TC_packet_methods` - Module that holds various methods that are used when constructing the MIB tables which are
      attributes of the :obj:`TC_packet.TC_packet` and :obj:`TC_packet.TC_header` classes.
    * :obj:`calib` - Module which holds classes that represent various types of calibrations/decalibrations/verifications which
      can occur in the C-files. It also holds methods that are used in the construction of these classes.
"""
