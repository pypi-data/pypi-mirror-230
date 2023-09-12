"""Parsing and structural interpretation module for C files. 

This module holds functions and classes serving the purpose of parsing C files containing information 
about the structure of packets and commands. The parsing in general happens mostly by recognising (a subset of)
standard C-syntax and the system of Python representations of C-objects tries to include all possible information
present in the C file, which makes it perhaps a bit too convoluted.
"""
import mib_generator.parsing.par_methods as parm

types = {"uint8_t", "uint16_t", "uint32_t", "uint64_t", "char", "unsigned int"}
typea = types.union({"struct"})


def str_parse(stri):
    """Parse the given string into blocks of "top-level" C-structures.

    By going iteratively through the string and recognising the features of standard C-syntax, this function
    first marks the positions of all C-objects (including ``#define`` macro declaration) and then creates an
    appropriate Python representation-object of them, which then at its initialisation further parses the
    inner structure of these objects. After going through the whole string, this function then returns all
    found C-objects in a list.

    Args:
        stri (str): A string to be parsed/analysed into the C-objects.

    Returns:
        list: List of Python representations of found C-objects, each represented by an object of child-class
        of :obj:`instance`

    """
    strc = parm.erase_text(stri)
    depth = 0
    structures = []
    start = 0
    typ = ""
    for i in range(len(stri)):
        if strc[i] not in {"c", "s", "u", ";", "}", "{", ")", "("}:
            pass
        elif depth == 0 and (
            (strc[i : i + 5] == "const" and strc[i + 7 :].startswith(tuple(typea)))
            or strc[i:].startswith(tuple(typea))
        ):
            start = i
            depth = 1
            for l in typea:
                if strc[i:].startswith(l) or (
                    strc[: i + 5] == "const" and strc[i:].startswith(l)
                ):
                    typ = l
        elif strc[i] == ";" and depth == 1:
            depth = 0
            if typ == "struct":
                structures.append(struct(typ, start, i - 1, stri[start:i]))
            else:
                structures.append(miscal(typ, start, i - 1, stri[start:i]))
        elif strc[i] in {"}", ")"}:
            depth -= 1
        elif strc[i] in {"{", "("}:
            depth += 1
    return structures


class instance_og:
    """Parent class of all representations of the C-objects.

    This class holds properties which are shared by all Python representations of C-objects found in the
    analysed file.

    Args:
        typ (str): The type of the C-object (e.g. ``struct`` or ``enum``).
        inds (int): Starting index of the C-object.
        inde (int): End index of the C-object.
        cont (str): Raw text of the C-object as in the source file.

    Attributes:
        type (str): The type of the C-object (e.g. ``struct`` or ``enum``).
        start (int): Starting index of the C-object.
        end (int): End index of the C-object.
        text (str): Raw text of the C-object as in the source file.
        comment (list): List holding all found interpretable comments associated to this C-object.
    """

    def __init__(self, typ, inds, inde, cont):
        self.type = typ
        self.start = inds
        self.end = inde
        self.text = cont
        self.comment = []


class instance(instance_og):
    """Class of "first order" C structure/object found in the body of the file.

    This class is a Python representation of an instance of a defined "top-level" object in the C-file. It does
    correspond to any specific type of such object (like ``struct``, ``uint8``, ...) unlike its child-classes,
    but rather holds general properties and methods that all of these classes need, like parsing into array of
    elements.

    All **parameters** are passed into the :obj:`instance_og` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the instance of a C-object.
        array (str): Equals to "-1" if the object isn't an array and otherwise denotes the number of elements
            found in the array. Either as an int number or some abstract expression to be evaluated later.
        elements (list): List of elements present if the structure is an array. Each of the elements is either
            of class :obj:`struct_r` or :obj:`misc_r`.
    """

    def __init__(self, typ, inds, inde, cont):
        instance_og.__init__(self, typ, inds, inde, cont)
        self.name, self.array, self.elements = self.str_parse(cont)
        if self.array != "-1":
            # this check doesn't make sense really because earlier I've assumed that we are given an array
            self.reposition()

    def str_parse(self, cont):
        """Parse the content of the C-object into its syntactic/semantic components.

        By first looking for whitespace characters and various types of brackets and then calling classes
        :obj:`struct_r` and :obj:`misc_r`, this function parses the text of the C-object into its name,
        array size and entries present.

        Args:
            cont (str): The raw text of the C-object as found in the C file.

        Returns:
            tuple: A tuple containing:

                * *str* - The name of the C-structure.
                * *str* - See the attribute :attr:`array` above.
                * *list* - See the attribute :attr:`elements` above.
        """
        x = parm.clean(cont, {"//", "\n", "/*", "*/"})
        if x[:6] == "const":
            x = x[7:]

        ind = x.find("=")
        head = x[len(self.type) + 1 : ind]
        body = x[ind + 1 :]
        if "[" in head and "]" in head:
            inds = head.find("[")
            inde = head.find("]")
            array = head[inds + 1 : inde]
            head = head[:inds] + head[inde + 1 :]
        else:
            array = "-1"
        depth = 0
        lis = []
        for i in range(len(body)):
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            if (body[i] in {",", "{"} and depth == 1) or (
                body[i] == "}" and depth == 0
            ):
                # this ugly thing takes care of trailing commas
                if not lis:
                    lis.append(i)
                else:
                    block = parm.clean(body[lis[-1] + 1 : i], {"\n", "\t"}).replace(
                        " ", ""
                    )
                    if len(block) > 2:
                        lis.append(i)
        elem = []
        for i in range(len(lis) - 1):
            start = self.start + ind + lis[i] + 2
            end = self.start + ind + lis[i + 1]
            text = body[lis[i] + 1 : lis[i + 1]]
            if self.type == "struct":
                elem.append(struct_r(self.type, start, end, text))
            else:
                elem.append(misc_r(self.type, start, end, text))
        return head, array, elem

    def reposition(self):
        """Use classic ordering if no specific position of each element of a structure is declared.

        The C-code at the level of instances of the structure in the array can contain information about a custom
        ordering inside this array. This is found while parsing the structure-instances, however if this
        information is not present, the default ordering has to be used instead which is what this function does
        by rewriting positions of the elements in the array in such case.
        """
        for i in range(len(self.elements)):
            if self.elements[i].position == "-1":
                self.elements[i].position = str(i)


class struct(instance):
    """Class of an instance of an array of structs.

    This class represents an instance of definition of a C-structure ``struct`` in the C-file. Being possibly
    an array of such structures, it inherits from :obj:`instance`, which already does most of the parsing, so
    at creation of this child-class only, some already parsed information are rewritten and corrected rather
    than the parsing happening from scratch.

    All **parameters** are passed into the :obj:`instance` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        flav (str): The type of the ``struct``, i.e. name of the ``struct`` declared possibly in the header
            of which this structure/array of structures is an instance.
        name (str): Corrected (from :obj:`instance`) name of the structure.
    """

    def __init__(self, typ, inds, inde, cont):
        instance.__init__(self, typ, inds, inde, cont)
        self.flav, self.name = self.add_parse(self.name)

    def add_parse(self, name):
        """Correct information about the object's name and type.

        Looks again at the string identified by :obj:`instance` as the object's name and if it seems wrong
        (e.g. whitespace characters occur in it) further parse it and extract the actual :attr:`name` and
        :attr:`flav` of the structure from it.

        Args:
            name (str): The possibly wrong name of the structure as recognised by the parser in :obj:`instance`

        Returns:
            tuple: A tuple containing:

                * *str* - The specific type of the structure. See :attr:`flav`.
                * *str* - The actual name of the structure.
        """
        inds = name.find(" ")
        nname = name[inds + 1 :].replace(" ", "")
        flav = name[:inds].replace(" ", "")
        for i in self.elements:
            i.name = flav
        return flav, nname


class miscal(instance):
    """Class of an instance of an array of constants.

    This class represents an instance of definition of a constant (e.g. ``unsigned integer``, ``uint16``, etc...)
    in the C-file. Being possibly an array of such objects, it inherits from :obj:`instance`, which already
    does most of the parsing, so at creation of this child-class, only some already parsed information are
    rewritten and corrected rather than the parsing happening from scratch.

    All **parameters** are passed into the :obj:`instance` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): Corrected (from :obj:`instance`) name of the object.
        array (str): Corrected (from :obj:`instance`) information about the array of the objects.
    """

    def __init__(self, typ, inds, inde, cont):
        instance.__init__(self, typ, inds, inde, cont)
        self.name = self.add_parse(self.name)

    def add_parse(self, name):
        """Correct information about the object's name.

        Looks again at the string identified by :obj:`instance` as the object's name, correct it (e.g. delete
        whitespace characters from it) and also save this name as a property :attr:`misc_r.flav` of each instance of
        the object in the array.

        Args:
            name (str): The possibly wrong name of the structure as recognised by the parser in :obj:`instance`

        Returns:
                str: The actual name of the structure.
        """
        nname = name.replace(" ", "")
        for i in self.elements:
            i.flav = nname
        return nname


class struct_r(instance_og):
    """Class of a singular instance of ``struct`` within an array.

    This class represents a specific instance of a C-structure inside a defined array. The contents of this
    instance are parsed (based on brackets and commas) such that the extracted information are the position
    of this instance inside the array and the contents of the defined array represented by a Python dictionary.

    All **parameters** are passed into the :obj:`instance_og` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        position (str): Position of the instance inside an array. Can be either a specific integer or an
            abstract expression to be interpreted later.
        entries (dict): A dictionary representing the defined contents of the instance of the ``struct``.
    """

    def __init__(self, typ, inds, inde, cont):
        instance_og.__init__(self, typ, inds, inde, cont)
        self.position, self.entries = self.srr_parse(cont)

    def srr_parse(self, cont):
        """Parse the ``struct`` instance into its entries.

        Based on the presence of "=", brackets and commas, this function recognises the presence of an identifier
        of the position of the structure instance (inside the array) and each of the entries inside the
        structure definitions. It then further interprets the former and creates a dictionary from the latter.

        Args:
            cont (str): Raw text of the C-code defining the object.

        Returns:
            tuple: A tuple containing:

                * *str* - Position of the instance. See :attr:`position`.
                * *dict* - A dictionary with the entries found in the ``struct`` instance.
        """
        if cont.find("=") < cont.find("{"):
            ind = cont.find("=")
            position = cont[:ind].replace(" ", "")
            cont = cont[ind + 1 :]
        else:
            position = "-1"
        depth = 0
        lis = []
        for i in range(len(cont)):
            if cont[i] == "{":
                depth += 1
            elif cont[i] == "}":
                depth -= 1
            if (cont[i] in {",", "{"} and depth == 1) or (
                cont[i] == "}" and depth == 0
            ):
                lis.append(i)
        elem = []
        for i in range(len(lis) - 1):
            elem.append(cont[lis[i] + 1 : lis[i + 1]])
        entr = {}
        for i in elem:
            ind = i.find("=")
            key = i[:ind].replace(" ", "")
            value = i[ind + 1 :].replace(" ", "")
            entr[key] = value
        return position, entr


class misc_r(instance_og):
    """Class of a singular instance of a constant within an array.

    This class represents a specific instance of a constant (e.g. ``unit32``, ...) inside a defined array.
    The contents of this instance are parsed (based on whitespace characters and "=") such that the
    extracted information are the position of this instance inside the array and the defined value of this
    instance.

    All **parameters** are passed into the :obj:`instance_og` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        position (str): Position of the instance inside an array. Can be either a specific integer or an
            abstract expression to be interpreted later.
        value (str): A value of this instance of the constant. Can be either a specific integer or an abstract
            expression to be interpreted later.
    """

    def __init__(self, typ, inds, inde, cont):
        instance_og.__init__(self, typ, inds, inde, cont)
        self.position, self.value = self.mis_parse(cont)

    def mis_parse(self, cont):
        """Parse the information about the constant instance.

        Based on the presence of "=" and whitespace characters this function recognises the presence
        of an identifier of the position of the constant instance (inside the array) and interprets the rest
        as the expression/value assigned to this instance.

        Args:
            cont (str): Raw text of the C-code defining the object instance.

        Returns:
            tuple: A tuple containing:

                * *str* - Position of the instance. See :attr:`position`.
                * *str* - A value of this instance of constant. See :attr:`value`.
        """
        if "=" in cont:
            ind = cont.find("=")
            position = cont[:ind].replace(" ", "")
            value = cont[ind + 1 :].replace(" ", "")
        else:
            position = "-1"
            value = cont.replace(" ", "")
        return position, value
