"""Depository of parsing methods.

This module holds various methods used for parsing of the header and normal C files and their
subsequent interpretation into corresponding python objects.
"""
import os

import json5

import mib_generator.data.warn as warn


def clean(stri, tokens):
    """Replace tokens with spaces.

    Takes a string and a list of tokens and replaces all occurences of the tokens in the string
    with an appropriate number of space so the absolute positions of unaffected parts of the
    string stay the same.

    Args:
        stri (str): A string to be "cleaned".
        tokens (set): A set of tokens to be replaced.

    Returns:
        str: The resulting "cleaned" string.
    """
    c = stri
    for i in tokens:
        c = c.replace(i, " " * len(i))
    return c


def erase_text(stri):
    """Erase all text inside quotation marks in the given string.

    Looks for first order quotation marks (that is, not inside another quotation marks) and
    replaces their content with matching amount of spaces so that the total length of the
    string remains the same.

    Args:
        stri (str): The string in which the quotation marks are to be replaced.

    Returns:
        str: The string with the quotation marks contents replaced.
    """
    mod = 0  # 0 for no quotation, 1 for ' and 2 for "
    new = stri
    for i in range(len(stri)):
        if stri[i] == '"' and mod != 2:
            if mod == 0:
                mod = 1
            else:
                mod = 0
        elif stri[i] == "'" and mod != 1:
            if mod == 0:
                mod = 2
            else:
                mod = 0
        elif mod != 0:
            new = new[:i] + " " + new[i + 1 :]
    return new


def line_index(stri):
    """Give list of indexes of line starts of the given string.

    Based on the newline character, looks for indexes of new lines and adds them to a list.

    Args:
        stri (str): The string to be analysed.

    Returns:
        list: List of indexes at which new lines start.
    """
    starts = []
    for i in range(len(stri)):
        if stri[i] == "\n":
            starts.append(i + 1)
    return starts


def split_comment(stri):
    """Split the given string into a section with C comments and a section without them.

    Goes iteratively through the string and based on single/multi-line C-comment syntax, recognised
    blocks of comments and marks their start/end positions. It then constructs versions of the passed
    string with the comment/code blocks ommited.

    Args:
        stri (str): The string to be split into comments/code.

    Returns:
        tuple: A tuple consisting of:
            * *str* - The original string with comments omitted.
            * *str* - The original string with C-code omitted.

    """
    mod = (
        0  # 0 for normal content, 1 for '...', 2 for "...", 3 for /* ...*/ and 4 for //
    )
    comm = ""
    cont = ""
    start = 0
    sections = []
    for i in range(
        len(stri)
    ):  # iterates through the string and marks different sections of it
        x = stri[i]
        xy = stri[i : i + 2]
        if x == '"' and mod == 2:
            mod = 0
        elif x == '"' and mod == 0:
            mod = 2
        elif x == "'" and mod == 1:
            mod = 0
        elif x == "'" and mod == 0:
            mod = 1
        elif xy == "/*" and mod == 0:
            mod = 3
            sections.append([start, i + 1])
        elif xy == "*/" and mod == 3:
            mod = 0
            sections.append([start, i - 1])
            start = i
        elif xy == "//" and mod == 0:
            mod = 4
            sections.append([start, i + 1])
            start = i + 2
        elif x == "\n" and mod == 4:
            mod = 0
            sections.append([start, i - 1])
            start = i
    if sections[-1][-1] != len(stri) - 1:
        sections.append([start, len(stri) - 1])
    switch = False  # keeps track of whether a given section is a content or a comment
    for i in sections:
        cut = stri[i[0] : i[1] + 1]
        if not switch:
            cont = cont + cut
            # comm = comm + " " * len(cut)
            if cut[:1] == "\n":  # horrible bodge which will come back to haunt me
                comm = comm + cut[:1] + " " * (len(cut) - 3) + cut[1:][-2:]
            else:
                comm = comm + cut[:2] + " " * (len(cut) - 4) + cut[2:][-2:]
        else:
            cont = cont + " " * len(cut)
            comm = comm + cut
        switch = not switch
    return cont, comm


def preproc_parse(stri):
    """Parse C-preprocessor conditional syntax into logic blocks.

    Looks for logical C-preprocessor directives (specifically ``#ifdef``, ``#ifndef``, etc.), and marks
    the start/end indices of the corresponding "logic blocks" (i.e. sections beween ``#ifdef`` and ``#else``).
    Then returns these block indexes in a list. Also performs some checks along the way.

    Args:
        stri (str): The string to be analysed/parsed.

    Returns:
        list: List of list of indexes denoting start/end positions of the logic blocks.
    """
    blocks = []
    log = []
    status = 0
    status_log = [0]
    for i in range(len(stri)):
        if stri[i : i + 6] == "#ifdef":
            log.append([i])
            status_log.append(status)
            status = 1
        elif stri[i : i + 7] == "#ifndef":
            log.append([i])
            status_log.append(status)
            status = 1
        elif stri[i : i + 5] == "#else":
            log[-1].append(i)
            if status != 1:
                warn.raises("WPM1")
            status = 2
        elif stri[i : i + 6] == "#endif":
            if status not in {1, 2}:
                warn.raises("WPM1")
            status = status_log.pop(-1)
            log[-1].append(i)
            blocks.append(log.pop(-1))
    if status != 0:
        warn.raises("WPM1")
    return blocks


def preproc_eval(variab):
    """Evaluate whether a pre-processing condition holds.

    Looks into config file whether the passed pre-processing condition holds. If the condition name
    does not occur in the config file, asks the user what boolean value it should assign to it.

    Args:
        variab (str): Name of the pre-processing variable/condition to be evaluated.

    Returns:
        bool: Truth-value of the condition.

    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "config.json5"
    )
    file = open(file_path, "r")
    config = json5.load(file)["def"]
    file.close()
    if variab in config.keys():
        return bool(config[variab])
    else:
        return bool(input("Is " + variab + "? (skip for False) "))


def preproc_filter(stri):
    """Filter out what parts of the C-code should be further considered based on preprocessor directives.

    First, this function looks for blocks pre-processor logic using the :obj:`preproc_parse` function. It then
    the condition associated with this logic with :obj:`preproc_eval` and depending on the result, decides what
    parts of the string should be deleted (replaced by equal number of spaces). Finally it performs this replacement.

    Args:
        stri (str): The text to be filtered on the basis of pre-processor logic.

    Returns:
        str: The text with the pre-processor logic applied.
    """
    blocks = preproc_parse(stri)
    filt = stri
    delete = []
    for i in blocks:
        condition = stri[i[0] : i[1]].split()[1]
        evalu = preproc_eval(condition)
        if stri[i[0] : i[1]].split()[0] == "#ifndef":
            evalu = not evalu
        if not evalu:
            delete.append([i[0], i[1]])
            if len(i) == 2:
                delete.append([i[1], i[1] + 6])
            else:
                delete.append([i[1], i[1] + 5])
                delete.append([i[2], i[2] + 6])
        else:
            if len(i) == 3:
                delete.append([i[1], i[2]])
                delete.append([i[2], i[2] + 6])
            else:
                delete.append([i[1], i[1] + 6])
            if stri[i[0] : i[1]].startswith("#ifdef"):
                delete.append([i[0], i[0] + 6])
            else:
                delete.append([i[0], i[0] + 7])
    for i in delete:
        filt = filt[: i[0]] + " " * (i[1] - i[0]) + filt[i[1] :]
    return filt


def com_parse(comm):
    """Parse the comments in the string into blocks corresponding to singular comments.

    Looks at each passed comment and evaluates whether it should be interpreted or not. If yes, it then calls
    the class :obj:`comment` from it and adds this object to the list of interpreted comments.

    Args:
        comm (list): List of strings each representing the content of a  single comment.

    Returns:
        list: List of found interpreted comments, each represented by an object of the :obj:`comment` class.
    """
    depth = 0
    start = 0
    blocks = []
    for i in range(len(comm)):
        if comm[i : i + 3] == "/*{" and depth == 0:
            start = i + 2
            depth = 1
        elif comm[i : i + 3] == "}*/" and depth == 1:
            blocks.append(comment(start, i, comm[start : i + 1]))
            depth = 0
        elif comm[i : i + 2] == "//" and depth == 0:
            depth = 2
        elif comm[i] == "\n" and depth == 2:
            depth = 0
    return blocks


class comment:
    """Class representing an occurrence of an interpretable comment in the file, entries found in it, etc.

    Saves the comment text and its start/end indexes and then it tries to interpret the comment as a dictionary
    represented in the json5 format.

    Args:
        start (int): Start index of the comment in the original file.
        end (int): End index of the comment in the original file.
        text (str): Original text of the comment.

    Attributes:
        start (int): Start index of the comment in the original file.
        end (int): End index of the comment in the original file.
        text (str): Original text of the comment.
        entries (dict): Dictionary containing the content of the comment found in the json5 string.
    """

    def __init__(self, start, end, text):
        self.text = text
        self.start = start
        self.end = end
        try:
            self.entries = json5.loads(text)
        except:
            warn.raises("EPM1", self.text)
            self.entries = {}
