"""A few mthods used by the GUI. They are mostly concerned with config files management.
"""
import os

import json5


def conf_to_json(typ):
    """Get a config parameter in a json5 format.

    This method looks up the config parameter of the passed ``typ`` in the runtime config files and if
    it finds it, it translates it to json5 string and returns it.

    Args:
        typ (str): The type/name of the config parameter to be looked up.

    Returns:
        str: A string json5 representation of the parameter value.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "config.json5"
    )
    fil = open(file_path, "r")
    dic = json5.load(fil)
    return json5.dumps(dic[typ])


def update_json(typ, data):
    """Update the runtime config file with the passed parameter.

    This method takes a config parameter with value ``data`` and of type/name ``typ``, loads the runtime
    config file, incorporates this parameter to it and then saves it again.

    Args:
        typ (str): The type/name of the config parameter to be saved.
        data (str): A json5 representation of the contents of the parameter to be saved.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "config.json5"
    )
    fil = open(file_path, "r")
    dic = json5.load(fil)
    fil.close()
    pdata = json5.loads(data)
    fil = open(file_path, "w")
    dic[typ] = pdata
    json5.dump(dic, fil)
    fil.close()
