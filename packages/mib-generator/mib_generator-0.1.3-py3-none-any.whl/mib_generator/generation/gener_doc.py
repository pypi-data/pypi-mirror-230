"""This module enables generation of a ``.docx`` file which documents in a human-readable way what was put in MIB tables for a
given set of Tm and Tc packets.

The only (important) method in this module builds up the ``.docx`` file using the not so powerful ``python-docx`` library.
"""

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches

import mib_generator.parsing.load as load


def gen_doc(Tm_packets=[], Tc_packets=[]):
    """Create a ``.docx`` document which sketches out what entries are in each of the Tm and Tc packets in the passed
    list.

    This method goes through all passed Tm and Tc packets and for each adds an entry to the created ``.docx`` document
    including basic info about the packet and a table of entries within it. The format of the output tries to adhere to a
    standard scheme of an ICD document used normally for these purposes.

    Args:
        Tm_packets (list): List of Tm-packets, each of type :obj:`mib_generator.construction.TM_packet.TM_packet`, from which
            the document is to be generated.
        Tc_packets (list): List of Tc-packets, each of type :obj:`mib_generator.construction.TC_packet.TC_packet`, from which
            the document is to be generated.

    """
    document = Document()
    if Tm_packets:
        document.add_heading("TM packets", 0)
    for i in Tm_packets:
        h = document.add_paragraph("")
        try:
            name = i.h_structure.comment[-1].entries["pack_type"]
        except:
            name = i.h_structure.name
        h.add_run(name + ": " + i.pid["PID_DESCR"]).italic = True
        table = document.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        table.rows[0].cells[0].paragraphs[0].add_run("Byte").bold = True
        table.rows[0].cells[1].paragraphs[0].add_run("ID").bold = True
        table.rows[0].cells[2].paragraphs[0].add_run("Size in bites").bold = True
        table.rows[0].cells[3].paragraphs[0].add_run("Description").bold = True
        for l in range(4):
            table.rows[0].cells[l]._tc.get_or_add_tcPr().append(
                parse_xml(r'<w:shd {} w:fill="C7D9F1"/>'.format(nsdecls("w")))
            )
            table.rows[0].cells[l].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for l in range(len(i.plf)):
            row = table.add_row().cells
            row[0].text = to_bytes(i.positions[l])
            row[1].text = i.pcf[l]["PCF_NAME"]
            row[2].text = str(i.positions[l + 1] - i.positions[l])
            row[3].text = i.pcf[l]["PCF_DESCR"]
            for k in range(4):
                row[k].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        document.add_paragraph()
    if Tc_packets:
        document.add_heading("TC packets", 0)
    for i in Tc_packets:
        h = document.add_paragraph("")
        h.add_run(i.ccf["CCF_DESCR2"]).italic = True
        table = document.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        table.rows[0].cells[0].paragraphs[0].add_run("Byte").bold = True
        table.rows[0].cells[1].paragraphs[0].add_run("ID").bold = True
        table.rows[0].cells[2].paragraphs[0].add_run("Size in bites").bold = True
        table.rows[0].cells[3].paragraphs[0].add_run("Type").bold = True
        table.rows[0].cells[4].paragraphs[0].add_run("Description").bold = True
        for l in range(5):
            table.rows[0].cells[l]._tc.get_or_add_tcPr().append(
                parse_xml(r'<w:shd {} w:fill="C7D9F1"/>'.format(nsdecls("w")))
            )
            table.rows[0].cells[l].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for l in range(len(i.cdf)):
            row = table.add_row().cells
            row[0].text = to_bytes(i.positions[l])
            row[1].text = i.cdf[l]["CDF_PNAME"]
            if not row[1].text:
                row[1].text = i.entries[l].name
            row[2].text = str(i.positions[l + 1] - i.positions[l])
            row[3].text = str(i.entries[l].type)
            row[4].text = i.cdf[l]["CDF_DESCR"]
            for k in range(4):
                row[k].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        document.add_paragraph()
    return document


def to_bytes(bits):
    """Give the number of bits in bytes and in some meaning full format.

    Calculates how many bytes are in the passed bits, how many residual bits, and puts together this information into a
    meaningful-looking string.

    Args:
        bits (int): Numeber of bits to be "translated".

    Returns:
        str: The number of bits in bytes and residual bits in understandable form.

    """
    byt = int(bits / 8)
    bit = bits - byt * 8
    if bit == 0:
        return str(byt)
    elif bit == 1:
        return str(byt) + " (+ " + str(bit) + " bit)"
    else:
        return str(byt) + " (+ " + str(bit) + " bits)"
