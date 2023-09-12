"""Parsing and structural interpretation module for C-header files. 

This module holds functions and classes serving the purpose of parsing C-header files containing information 
about the structure of packets and commands. The parsing in general happens mostly by recognising (a subset of)
standard C-syntax and the system of Python representations of C-objects tries to include all possible information
present in the C-header file, which makes it perhaps a bit too convoluted.
"""
import mib_generator.parsing.par_methods as parm

types = {"uint8_t", "uint16_t", "uint32_t", "uint64_t", "char", "unsigned int"}


def str_parse(stri):
    """Parse the given string into blocks of "top-level" C-structures.

    By going iteratively through the string and recognising the features of standard C-syntax, this function
    first marks the positions of all C-objects (including ``#define`` macro declaration) and then creates an
    appropriate Python representation-object of them, which then at its initialisation further parses the inner structure of these
    objects. After going through the whole string, this function then returns all found C-objects in a list.

    Args:
        stri (str): A string to be parsed/analysed into the C-objects.

    Returns:
        list: List of Python representations of found C-objects, each represented by an object of child-class
        of :obj:`structure`

    """
    strc = parm.erase_text(stri)
    depth = 0
    structures = []
    start = 0
    typ = ""
    for i in range(len(stri)):
        if strc[i] not in {"#", "e", "s", ";", "\n", "}", "{", ")", "("}:
            pass
        elif strc[i : i + 7] == "#define" and depth == 0:
            start = i
            depth = 1
            typ = "define"
        elif strc[i : i + 4] == "enum" and depth == 0:
            start = i
            depth = 1
            typ = "enum"
        elif strc[i : i + 6] == "struct" and depth == 0:
            start = i
            depth = 1
            typ = "struct"
        elif strc[i : i + 6] == "extern" and depth == 0:
            start = i
            depth = 1
            typ = "extern"
        elif strc[i] == "\n" and depth == 1 and typ == "define":
            depth = 0
            structures.append(define(typ, start, i - 1, stri[start:i]))
        elif strc[i] == ";" and depth == 1 and typ in {"extern", "struct", "enum"}:
            depth = 0
            if typ == "extern":
                structures.append(extern(typ, start, i - 1, stri[start:i]))
            elif typ == "enum":
                structures.append(enum(typ, start, i - 1, stri[start:i]))
            elif typ == "struct":
                structures.append(struct(typ, start, i - 1, stri[start:i]))
        elif strc[i] in {"}", ")"}:
            depth -= 1
        elif strc[i] in {"{", "("}:
            depth += 1
    return structures


def str_parse_r(offset, stri):
    """Parse the given string into "2nd-order" blocks of C-structures.

    Unlike for :obj:`str_parse` this time "second-order" strings (that is strings inside other already recognised
    C-objects; i.e. e.g. inner content of ``struct`` declaration) are expected and the parsing itslef is recursive
    (in order to account e.g. for multiple nested occurences of ``struct``).

    Args:
        offset (int): Offset of this string from the start of the original file. I.e. original start index of its
            first character.
        stri (str): The string to be parsed/interpreted into its contents.

    Returns:
        list:
            List of identified and interpreted C-object inside the original string. Each is represented by an
            object which is some child-class of the class :obj:`structure`.
    """
    strc = parm.erase_text(stri)
    depth = 0
    structures = []
    start = 0
    typ = ""
    for i in range(len(stri)):
        if strc[i] not in {"e", "s", ";", "\n", "}", "{", ")", "(", "u", "c"}:
            pass
        elif strc[i : i + 4] == "enum" and depth == 0:
            start = i
            depth = 1
            typ = "enum"
        elif strc[i : i + 6] == "struct" and depth == 0:
            start = i
            depth = 1
            typ = "struct"
        elif strc[i:].startswith(tuple(types)) and depth == 0:
            start = i
            depth = 1
            for l in types:
                if strc[i:].startswith(l):
                    typ = l
        elif strc[i] == ";" and depth == 1:
            depth = 0
            if typ == "enum":
                structures.append(
                    enum_r(typ, offset + start, offset + i - 1, stri[start:i])
                )
            elif typ == "struct":
                structures.append(
                    struct_r(typ, offset + start, offset + i - 1, stri[start:i])
                )
            else:
                structures.append(
                    misc_r(typ, offset + start, offset + i - 1, stri[start:i])
                )
        elif strc[i] in {"}", ")"}:
            depth -= 1
        elif strc[i] in {"{", "("}:
            depth += 1
    return structures


class structure:
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


class enum(structure):
    """Class of an ``enum`` C-object.

    This class is a Python representation of an occurrence of ``enum`` in the C-header file. The inner
    structure of the ``enum`` is parsed and represented as a Python dictionary.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): Name of the ``enum`` object.
        entries (dict): Dictionary containing key-value pairs found in the ``enum``.
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.entries = self.ele_parse(cont)

    def ele_parse(self, cont):
        """Parse ``enum`` into its syntactic/semantic components.

        By recognising and parsing the inner syntax of ``enum`` this function identifies all elements in it
        and the values assigned to them (be it directly or implicitly by the order of the elements ``enum``).
        Subsequently it represents these key-value pairs by a Python dictionary.

        Args:
            cont (str): Text of the whole ``enum`` object.

        Returns:
            tuple: A tuple containing:

                * *str* - The name of the ``enum``.
                * *dict* - A dictionary representing the entries in the ``enum`` and the values/expressions assigned to them.
        """
        x = parm.clean(cont, {"enum", "//", "\n", "/*", "*/"})
        x = x.replace(" ", "")
        brack = 0
        comma = []
        for i in range(len(x)):
            if x[i] == "{":
                brack = i
            elif x[i] == ",":
                comma.append(i)
        name = x[:brack]
        comma = [brack] + comma + [len(x) - 1]
        # takes care of trailing commas
        if comma[-1] - comma[-2] < 2:
            comma.pop(-1)
        elem = []
        for i in range(len(comma) - 1):
            elem.append(x[comma[i] + 1 : comma[i + 1]])
        numb = []
        keys = []
        for i in elem:
            if "=" in i:
                position = i.find("=")
                try:
                    numb.append(int(i[position + 1 :]))
                except:
                    numb.append(int(i[position + 1 :]))
                keys.append(i[:position])
            else:
                if len(numb) != 0:
                    numb.append(numb[-1] + 1)
                else:
                    numb.append(0)
                keys.append(i)
        return name, dict(zip(keys, numb))


class define(structure):
    """Class of a ``#define`` makro.

    This class is a Python representation of an occurrence of ``#define`` macro in the C-header file. The inner
    structure of the macro is parsed and represented as a name and an expression.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the definition in the macro.
        expression (str): A string with the expression or value that the macro points to.
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.expression = self.def_parse(cont)

    def def_parse(self, cont):
        """Parse the ``#define`` macro into its syntactic/semantic components.

        By looking for whitespace characters, parses the text of the macro into its name and the expression it
        points to.

        Args:
            cont (str): The text of the macro.

        Returns:
            tuple: A tuple containing:

                * *str* - The name of the macro.
                * *str* - The expression the macro points to.
        """
        x = parm.clean(cont, {"//", "\n", "/*", "*/"})
        x = x[8:]
        if " " in x:
            ind = x.find(" ")
            return x[:ind], x[ind + 1 :]
        else:
            return x, ""


class extern(structure):
    """Class of external declaration of a constant.

    This class is a Python representation of an occurrence of external constant declaration in the C-header
    file. The inner structure of the expression is parsed and represented as its name, type (e.g. ``uint8``)
    and an information on whether it is an array.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the external declaration.
        flav (str): The data type of the declaration (e.g. ``"uint8"``)
        array (str): An expression set to "-1" if the declared constant is not an array and to its number of
            elements (either integer value or an text expression to be later evaluated) in case it is an array.
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.flav, self.name, self.array = self.ext_parse(cont)

    def ext_parse(self, cont):
        """Parse the external declaration of a constant into its syntactic/semantic components.

        By looking for whitespace characters and square brackets, parses the text of the declaration into its
        name, data type and n information on whether it is an array.

        Args:
            cont (str): The text of the declaration to be parsed.

        Returns:
            tuple: A tuple containing:

                * *str* - The data type of the declaration (e.g. ``"unsigned integer"``).
                * *str* - The name of the declaration.
                * *str* - The information on its array size (see above for more detail).
        """
        x = parm.clean(cont, {"//", "\n", "/*", "*/"})
        x = x[13:]
        ind = x.find(" ")
        part_1 = x[:ind]
        x = x[ind + 1 :]
        if " " in x:
            ind = x.find(" ")
            part_2 = " " + x[:ind]
            x = x[ind + 1 :]
        else:
            part_2 = ""
        if "[" in x and "]" in x:
            ind = x.find("[")
            part_3 = x[:ind]
            inde = x.find("]")
            part_4 = x[ind + 1 : inde]
        else:
            part_3 = x
            part_4 = "-1"
        return part_1 + part_2, part_3, part_4


class struct(structure):
    """Class of declaration of a C-structure ``struct ...``.

    This class is a Python representation of an occurrence of ``struct`` structure in the C-header file. The inner
    structure of this ... structure is represented by its name, information on whether it is packed and its
    contents/elements (which are themselves other similar Python objects).

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the structure.
        packed (bool): True if the structure is packed, false otherwise.
        elements (list): A list of elements inside this structure. Each is represented by a Python object which is
            some child-class of :obj:`structure`
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.packed, self.elements = self.stc_parse(cont)

    def stc_parse(self, cont):
        """Parse the ``struct`` C-structure into its syntactic/semantic components.

        By first looking for whitespace characters and "{" and then calling :obj:`str_parse_r`, this function parses
        the text of the ``struct`` object into its name, entries, etc.

        Args:
            cont (str): The raw text of the ``struct`` C-structure in the C-header file.

        Returns:
            tuple: A tuple containing:

                * *str* - The name of the C-structure.
                * *bool* - ``True`` if the structure is packed, ``False`` otherwise.
                * *list* - List of elements inside the structure. Each represented by an object of
                  child-class of :obj:`structure`.
        """
        x = parm.clean(cont, {"//", "\n", "/*", "*/"})
        x = x[7:]
        ind = x.find("{")
        head = x[:ind]
        body = x[ind + 1 : -1]
        if "PACKED" in head:
            packed = True
            name = head[7:].replace(" ", "")
        else:
            packed = False
            name = head.replace(" ", "")
        entries = str_parse_r(ind + 8 + self.start, body)
        return name, packed, entries


class struct_r(structure):
    """Class of a reference to a C-structure ``struct`` inside another.

    This class is used to represent occurrence of declaration of one structure inside another. It can be of two types:

        1. It is only a reference to a structure defined elsewhere. In this case, the :attr:`form` attribute holds the
           name of this reference.
        2. There is a nested definition of one structure inside another. In this case, an object of class :obj:`struct` is
           used to represent the included structure and it is equated to :obj:`form`.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the referenced C-structure.
        form (str or struct): Either name of the referenced structure or directly the object of the referenced structure.
        array (str): An expression set to "-1" if the ``struct`` reference is not an array and to its number of
            elements (either integer value or an text expression to be later evaluated) in case it is an array.
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.form, self.array = self.str_parse(cont)

    def str_parse(self, cont):
        """Parse the reference to its syntactic/semantic components.

        By looking for "{" and "}" this function first decides whether the references includes a nested structure or only
        and external reference. Depending on the result it either calls the class :obj:`struct` or leaves the reference as
        a text. It then continues by looking for the name, array information, etc by looking at the whitespaces and brackets.

        Args:
            cont (str): The text of the structure reference to be analysed.

        Returns:
            tuple: A tuple consisting of:

                * *str* - The name of the referenced structure.
                * *str* or :obj:`struct` - See the attribute :attr:`form` above.
                * *str* - See the attribute :attr:`array` above.

        """
        if "{" not in cont or "}" not in cont:
            x = cont[7:]
            ind = x.find(" ")
            if ind > 0:
                form = x[:ind]
                rest = x[ind + 1 :]
            else:
                if "[" in x:
                    indb = x.find("[")
                    form = x[:indb]
                    rest = x[indb:]
                else:
                    form = x
                    rest = ""
        else:
            ind = cont.rfind("}")
            form = struct("struct", self.start, self.start + ind + 1, cont[: ind + 1])
            rest = cont[ind + 1 :]
        if "[" in rest and "]" in rest:
            ind = rest.find("[")
            inde = rest.find("]")
            array = rest[ind + 1 : inde]
            rest = rest[:ind] + rest[inde + 1 :]
        else:
            array = "-1"
        return rest.replace(" ", ""), form, array


class enum_r(structure):
    """Class of a reference to an ``enum`` inside a C-structure.

    This class is used to represent occurrence of reference to ``enum`` inside a C-structure (a ``struct`` object). It can
    be of two types:

        1. It is only a reference to an ``enum`` defined elsewhere. In this case, the :attr:`form` attribute holds the
           name of this reference.
        2. There is a nested definition of the ``enum`` inside this C-structure. In this case, an object of class :obj:`enum` is
           used to represent the included ``enum`` and it is equated to :obj:`form`.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the referenced ``enum``.
        form (str or enum): Either name of the referenced ``enum`` or directly the object of the referenced ``enum``.
        bites (int): Number of bites that the value of this ``enum`` is represented by.
        array (str): An expression set to "-1" if the ``enum`` reference is not an array and to its number of
            elements (either integer value or an text expression to be later evaluated) in case it is an array.

    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.form, self.bites, self.array = self.enr_parse(cont)

    def enr_parse(self, cont):
        """Parse the reference to its syntactic/semantic components.

        By looking for "{" and "}" this function first decides whether the references includes a nested ``enum`` or only
        and external reference. Depending on the result it either calls the class :obj:`enum` or leaves the reference as
        a text. It then continues by looking for the name, array and bites information, etc by looking at the whitespaces and brackets.

        Args:
            cont (str): The text of the ``enum`` reference to be analysed.

        Returns:
            tuple: A tuple consisting of:

                * *str* - The name of the referenced ``enum``.
                * *str* or :obj:`struct` - See the attribute :attr:`form` above.
                * *int* - See the atribute :attr:`bite` above.
                * *str* - See the attribute :attr:`array` above.

        """
        if "{" not in cont or "}" not in cont:
            x = cont[5:]
            ind = x.find(" ")
            form = x[:ind]
            rest = x[ind + 1 :]
        else:
            ind = cont.rfind("}")
            form = enum("enum", self.start, self.start + ind + 1, cont[: ind + 1])
            rest = cont[ind + 1 :]
        if "[" in rest and "]" in rest:
            ind = rest.find("[")
            inde = rest.find("]")
            array = rest[ind + 1 : inde]
            rest = rest[:ind] + rest[inde + 1 :]
        else:
            array = "-1"
        if ":" in rest:
            ind = rest.find(":")
            try:
                byte = int(rest[ind + 1 :].replace(" ", ""))
                rest = rest[:ind]
            except:
                byte = -1
        else:
            byte = -1
        return rest.replace(" ", ""), form, byte, array


class misc_r(structure):
    """Class of a declaration of a constant inside a C-structure.

    This class is a Python representation of an occurrence of constant value declaration (e.g. ``uint8``) inside
    of some C-structure . The inner structure of the expression is parsed and represented as its name, bite length
    and an information on whether it is an array.

    All **parameters** are passed into the :obj:`structure` class from which this structure also inherits all
    its **attributes**.

    Attributes:
        name (str): The name of the declared constant.
        bites (int): Number of bites that the value of this constant is represented by.
        array (str): An expression set to "-1" if the constant is not an array and to its number of
            elements (either integer value or an text expression to be later evaluated) in case it is an array.
    """

    def __init__(self, typ, inds, inde, cont):
        super().__init__(typ, inds, inde, cont)
        self.name, self.bites, self.array = self.mir_parse(cont)

    def mir_parse(self, cont):
        """Parse the declaration into its syntactic/semantic components.

        By looking at whitspaces and brackets in the string this function parses the text of the declaration into
        the name of the constant, and information about its bite-length and array-size.

        Args:
            cont (str): The text of the constant declaration.

        Returns:
            tuple: A tuple containing:

                * *str* - The name of the constant.
                * *int* - The declared bite-length of the constant.
                * *str* - See the attribute :attr:`array` above.
        """
        rest = cont[len(self.type) + 1 :]
        if "[" in rest and "]" in rest:
            ind = rest.find("[")
            inde = rest.find("]")
            array = rest[ind + 1 : inde]
            rest = rest[:ind] + rest[inde + 1 :]
        else:
            array = "-1"
        if ":" in rest:
            ind = rest.find(":")
            try:
                byte = int(rest[ind + 1 :].replace(" ", ""))
                rest = rest[:ind]
            except:
                byte = -1
        else:
            byte = -1
        return rest.replace(" ", ""), byte, array
