"""The main GUI module.

This module initialises and runs the GUI for the program which uses the Qt framework. The majority of the GUI structure is declared
in the :obj:`mib_generator.gui.ui_form` module and here the main-window class :obj:`MainWindow` contains mostly the logic interconnecting
various parts of the GUI and their connections to the main program itself (the documentation of :obj:`MainWindow` is not in Sphinx right now because of a bug
in PySide6).
"""
import os
import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow

# Adds the mib-generator package to path so that it can be accessed even if not installed through pip
file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(file_path)

import mib_generator.construction.calib as calib
import mib_generator.construction.TC_packet as tc_packet
import mib_generator.construction.TC_packet_methods as tc_packet_methods
import mib_generator.construction.TM_packet as tm_packet
import mib_generator.construction.TM_packet_methods as tm_packet_methods
import mib_generator.data.warn as warn
import mib_generator.generation.gener as gener
import mib_generator.generation.gener_doc as generd
import mib_generator.gui.gui_methods as gm
import mib_generator.parsing.load as load
import mib_generator.temp.temp as temp
import mib_generator.utilities.visualiser as visualiser
from mib_generator.gui.ui_form import Ui_MainWindow

# Important:
# You need to run the following command (in the GUI directory) to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or


class MainWindow(QMainWindow):
    """Class holding the whole structure and logic of the GUI.

    This class represents the main window of the GUI and all of its functions. The layout of the GUI
    is imported from the :obj:`mib_generator.gui.ui_form.Ui_MainWindow` class so bellow only functions
    of all of the elements of the GUI are described with all corresponding methods.

    (this docstring is not shown in Sphinx documentation because of a bug in PySide6<6.6.0)

    Args:
        parent (object): The parent widget of the window. (``None`` if run standalone and default)

    Attributes:
        ui (object): A class imported from :obj:`mib_generator.gui.ui_form` which holds layout and representations
            of all elements of the GUI.
        tms (list): List of TM packet representations created/used by the program. Each of type
            :obj:`mib_generator.construction.TM_packet.TM_packet`.
        TmHead (construction.TM_packet.TM_header): TM header representation created/used by the program.
        tcs (list): List of TC packet/command representations created/used by the program. Each of type
            :obj:`mib_generator.construction.TC_packet.TC_packet`.
        TcHead (construction.TC_packet.TC_header): TC header representation created/used by the program.
        cal (dict): A dictionary of lists of calibration representations created/used by the program. Each of
            type :obj:`mib_generator.construction.calib.calib`.
        dec (list): A list of decalibration representations created/used by the program. Each of type
            :obj:`mib_generator.construction.calib.decalibration`.
        ver (list): A list of verification representations created/used by the program. Each of type
            :obj:`mib_generator.construction.calib.verification`.
        tables (dict): A dictionary holding various MIB tables constructed by the program.
        docum (docx.document): A ``.docx`` document constructed by the program from the list of TM and TC packets.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIB Generator")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("MIB Generator")

        warn.disp_update(self.ui.console)
        self.tms = None
        self.TmHead = None
        self.tcs = None
        self.TcHead = None
        self.cal = None  # {"mcfs": [], "txfs": [], "cafs": [], "lgfs": []}
        self.dec = None
        self.ver = None
        self.tables = {}
        self.docum = None

        self.ui.parsebutton.clicked.connect(self.parse)
        self.ui.TmHview.clicked.connect(self.TmHshow)
        self.ui.TcHview.clicked.connect(self.TcHshow)
        self.ui.TmCview.clicked.connect(self.TmCshow)
        self.ui.TcTmHview.clicked.connect(self.TcTmHshow)
        self.ui.Tmbuild.clicked.connect(self.Tminter)
        self.ui.Tcbuild.clicked.connect(self.Tcinter)
        self.ui.mibgen.clicked.connect(self.MIBgen)
        self.ui.docgen.clicked.connect(self.DOCgen)
        self.ui.mibsave.clicked.connect(self.MIBsave)
        self.ui.docsave.clicked.connect(self.DOCsave)
        self.ui.compute_all.clicked.connect(self.compute)
        self.ui.TmHbutton.clicked.connect(lambda: self.Cfile(self.ui.TmHfield))
        self.ui.TcHbutton.clicked.connect(lambda: self.Cfile(self.ui.TcHfield))
        self.ui.TmCbutton.clicked.connect(lambda: self.Cfile(self.ui.TmCfield))
        self.ui.TcTmHbutton.clicked.connect(lambda: self.Cfile(self.ui.TcTmHfield))
        self.ui.outdirbutton.clicked.connect(lambda: self.direc(self.ui.outdirfield))
        self.ui.outdocbutton.clicked.connect(self.Dfile)
        self.ui.configbutton.clicked.connect(lambda: self.direc(self.ui.configfield))
        self.ui.pathsbutton.clicked.connect(self.use_paths)
        self.ui.configdefault.clicked.connect(self.def_config)
        self.ui.configload.clicked.connect(self.load_config)
        self.ui.configsave.clicked.connect(self.save_config)
        self.ui.mibbutton.clicked.connect(self.mib_use)
        self.ui.prebutton.clicked.connect(self.pre_set)

        try:
            self.ui.configdefault.click()
            self.ui.configload.click()
        except:
            pass

    @Slot()
    def compute(self):
        """Click all computation buttons in sequential order.

        This links all the computation to one button, be clicking of which the user effectively clicks
        all of the computational buttons (if they are disabled, then nothing happens) sequentially.
        """
        self.ui.parsebutton.click()
        self.ui.Tmbuild.click()
        self.ui.Tcbuild.click()
        self.ui.mibgen.click()
        self.ui.docgen.click()
        self.ui.mibsave.click()
        self.ui.docsave.click()

    @Slot()
    def parse(self):
        """Runs the parsing logic and modifies the GUI correspondingly.

        This module runs all the parsing from the :obj:`mib_generator.parsing.load` module and then depending
        on the results for each file either enables or disables GUI buttons that would run subsequent computation or
        show the parsing results. Also raises warnings/errors if anything fails.
        """
        try:
            load.load_all()
            if load.TmH:
                self.ui.TmHview.setEnabled(True)
                self.ui.TmHview.setText("View")
            else:
                self.ui.TmHview.setEnabled(False)
                self.ui.TmHview.setText("Error")
            if load.TcH:
                self.ui.TcHview.setEnabled(True)
                self.ui.TcHview.setText("View")
                self.ui.Tcbuild.setEnabled(True)
            else:
                self.ui.TcHview.setEnabled(False)
                self.ui.TcHview.setText("Error")
                self.ui.Tcbuild.setEnabled(False)
            if load.TmC:
                self.ui.TmCview.setEnabled(True)
                self.ui.TmCview.setText("View")
            else:
                self.ui.TmCview.setEnabled(False)
                self.ui.TmCview.setText("Error")
            if load.TcTmH:
                self.ui.TcTmHview.setEnabled(True)
                self.ui.TcTmHview.setText("View")
            else:
                self.ui.TcTmHview.setEnabled(False)
                self.ui.TcTmHview.setText("Error")
            if load.TmH and load.TmC:
                self.ui.Tmbuild.setEnabled(True)
            else:
                self.ui.Tmbuild.setEnabled(False)
            warn.raises("CGU6")
        except:
            warn.raises("EGU6")

    @Slot()
    def TmHshow(self):
        """Show GUI representations of parsed ``Tm .h`` file.

        Opens new window with visual representation of what the parser found/interpreted inside the ``Tm .h`` file.
        """
        try:
            self.prewTmH = visualiser.MainWindow(load.TmH)
            self.prewTmH.show()
        except:
            warn.raises("EGUD", "Tm .h")

    @Slot()
    def TcHshow(self):
        """Show GUI representations of parsed ``Tc .h`` file.

        Opens new window with visual representation of what the parser found/interpreted inside the ``Tc .h`` file.
        """
        try:
            self.prewTcH = visualiser.MainWindow(load.TcH)
            self.prewTcH.show()
        except:
            warn.raises("EGUD", "Tc .h")

    @Slot()
    def TmCshow(self):
        """Show GUI representations of parsed ``Tm .c`` file.

        Opens new window with visual representation of what the parser found/interpreted inside the ``Tm .c`` file.
        """
        try:
            self.prewTmC = visualiser.MainWindow(load.TmC)
            self.prewTmC.show()
        except:
            warn.raises("EGUD", "Tm .c")

    @Slot()
    def TcTmHshow(self):
        """Show GUI representations of parsed ``TcTm .h`` file.

        Opens new window with visual representation of what the parser found/interpreted inside the ``TcTm .h`` file.
        """
        try:
            self.prewTcTmH = visualiser.MainWindow(load.TcTmH)
            self.prewTcTmH.show()
        except:
            warn.raises("EGUD", "TcTm .h")

    @Slot()
    def Tminter(self):
        """Interpret the Tm packets found in the parsed files.

        This method runs the code from the :obj:`mib_generator.construction` module which interprets the parsed files
        relating to TM packets and constructs appropriate Python representations of the included objects from them.
        It updates the list of calibrations :attr:`cal`, list of TM packets :attr:`tms` and the TM header :attr:`TmHead`.
        It also enables buttons for subsequent computation if everything runs correctly.
        """
        try:
            cal1 = calib.calib_extract(load.TmH.comments)
            cal2 = calib.calib_extract(load.TcTmH.comments)
            self.cal = {i: cal1[i] + cal2[i] for i in cal1}
            self.TmHead = tm_packet.TM_header(load.TmH)
            self.tms = []
            for i in load.TmC.structures[1].elements:
                matched = tm_packet_methods.header_search(i.entries[".type"])
                for k in matched:
                    pack = tm_packet.TM_packet(i, k, self.TmHead)
                    calib.cur_update(pack, self.cal)
                    self.tms.append(pack)
            self.ui.mibgen.setEnabled(True)
            self.ui.docgen.setEnabled(True)
            warn.raises("CGU7")
        except:
            warn.raises("EGU7")

    @Slot()
    def Tcinter(self):
        """Interpret the Tc packets/commands found in the parsed files.

        This method runs the code from the :obj:`mib_generator.construction` module which interprets the parsed files
        relating to TC packets and constructs appropriate Python representations of the included objects from them.
        It updates the list of decalibrations :attr:`dec`, verifications :attr:`ver`, the list of TC packets/commands
        :attr:`tcs` and the TC header :attr:`TcHead`. It also enables buttons for subsequent computation if everything
        runs correctly.
        """
        try:
            dec1 = calib.decal_extract(load.TcH.comments)
            dec2 = calib.decal_extract(load.TcTmH.comments)
            self.dec = dec1 + dec2
            ver1 = calib.verif_extract(load.TcH.comments)
            ver2 = calib.verif_extract(load.TcTmH.comments)
            self.ver = ver1 + ver2
            self.TcHead = tc_packet.TC_header(tc_packet_methods.find_header(load.TcH))
            packets = tc_packet_methods.packet_search(load.TcH)
            self.tcs = []
            for i in packets:
                comm = tc_packet.TC_packet(i, self.TcHead)
                calib.cpc_update(comm, self.dec)
                calib.cvs_update(comm, self.ver)
                self.tcs.append(comm)
            self.ui.mibgen.setEnabled(True)
            self.ui.docgen.setEnabled(True)
            warn.raises("CGU8")
        except:
            warn.raises("EGU8")

    @Slot()
    def MIBgen(self):
        """Generates MIB tables based on all computation done so far.

        With all so far constructed representations (Tm packets, Tc commands, calibrations, etc...) taken into
        account as well as used config settings, generates the corresponding MIB tables. Also adjusts the GUI
        appropriately based on the result and saves the generation output to the :attr:`tables` attribute.
        """
        try:
            self.tables = gener.generation_hub(
                self.tms, self.tcs, self.cal, self.dec, self.ver, self.TcHead
            )
            self.ui.mibsave.setEnabled(True)
            warn.raises("CGU9")
        except:
            self.tables = {}
            self.ui.mibsave.setEnabled(False)
            warn.raises("EGU9")

    @Slot()
    def DOCgen(self):
        """Generates a ``.docx`` document summing up the results of the construction process.

        Takes the list of representations of TC and TM packets and  generates an entry in a ``.docx`` document
        based on each of them. It then assigns this value to the :attr:`docum` attribute.
        """
        try:
            self.docum = generd.gen_doc(self.tms, self.tcs)
            self.ui.docsave.setEnabled(True)
            warn.raises("CGUA")
        except:
            self.docum = None
            self.ui.docsave.setEnabled(False)
            warn.raises("EGUA")

    @Slot()
    def MIBsave(self):
        """Save the generated MIB tables to ``.dat`` files.

        Looks up the directory where the tables should be saved to in the runtime config files and saves them there.
        """
        try:
            gener.save_tables(self.tables)
            warn.raises("CGUB")
        except:
            warn.raises("EGUB")

    @Slot()
    def DOCsave(self):
        """Save the generated ``.docx`` document .

        Looks up the location where the document should be saved to and saves it ther.
        """
        try:
            self.docum.save(load.out_doc)
            warn.raises("CGUC")
        except:
            warn.raises("EGUC")

    @Slot()
    def Cfile(self, field):
        """Open a dialog for choosing a file and use the output.

        Opens a system dialog for choosing file and lets the user choose an input ``.c/.h`` file  through
        it. It then assigns the path to the chosen location to the passed text field.

        Args:
            field (PySide6.QtWidgets.QPlainTextEdit): A text window to which the outputted location is to be filled.
        """
        ftype = "C files (*.c *.h)"
        base = os.path.dirname(field.text())
        file = QFileDialog.getOpenFileName(self, "Choose file", base, ftype)
        if file[0] != "":
            field.setText(file[0])

    @Slot()
    def direc(self, field):
        """Open a dialog for choosing a directory and use the output.

        Opens a system dialog for choosing a directory and lets the user choose an output directory  through
        it. It then assigns the path to the chosen location to the passed text field.

        Args:
            field (PySide6.QtWidgets.QPlainTextEdit): A text window to which the outputted location is to be filled.
        """
        base = os.path.dirname(field.text())
        capt = "Choose a directory"
        file = QFileDialog.getExistingDirectory(self, capt, base)
        if file != "":
            field.setText(file)

    @Slot()
    def Dfile(self):
        """Open a dialog for choosing a file and use the output.

        Opens a system dialog for choosing file and lets the user choose an input ``.docx`` file  through
        it. It then assigns the path to the chosen location to the ``.docx`` path text field.
        """
        ftype = "Microsoft Word files (*.docx)"
        base = os.path.dirname(self.ui.outdocfield.text())
        file = QFileDialog.getSaveFileName(self, "Choose file", base, ftype)
        if file[0] != "":
            self.ui.outdocfield.setText(file[0])

    @Slot()
    def use_paths(self):
        """Use the paths specified in the input field.

        Gets all the contents of the paths input fields, saves them to the runtime config files found in the
        :obj:`mib_generator.temp` sub-package/directory and loads them. Raises various warnings if anything goes
        wrong.
        """
        try:
            dic = {
                "TmHeader": self.ui.TmHfield.text(),
                "TcTmHeader": self.ui.TcTmHfield.text(),
                "TmFile": self.ui.TmCfield.text(),
                "TcHeader": self.ui.TcHfield.text(),
                "OutDir": self.ui.outdirfield.text(),
                "OutDoc": self.ui.outdocfield.text(),
            }
            dictn = temp.update_paths(dic)
            load.get_paths()
            self.dist_paths(dictn)
            warn.raises("CGU2")
        except:
            warn.raises("EGU2")

    @Slot()
    def def_config(self):
        """Fill in the path to default config directory to the config directory field.

        Gets path to the default config location (it is the :obj:`mib_generator.data` sub-package/directory)
        and fills it to the config directory input text field.
        """
        try:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            self.ui.configfield.setText(file_path)
            warn.raises("CGU1")
        except:
            warn.raises("EGU1")

    @Slot()
    def load_config(self):
        """Load all data from config files in the specified directory.

        This method first looks for config files in the specified directory, if it finds any, it copies them
        to the runtime config directory and from there loads their content to all the appropriate text fields
        in the GUI.
        """
        try:
            if os.path.isdir(self.ui.configfield.text()):
                temp.move_conf(self.ui.configfield.text())
                load.get_paths()
                self.dist_paths(temp.fetch_paths())
                self.ui.mibfield.setPlainText(gm.conf_to_json("mib"))
                self.ui.prefield.setPlainText(gm.conf_to_json("def"))
                warn.raises("CGU4")
            else:
                warn.raises("WGU1", self.ui.configfield.text())
        except:
            warn.raises("EGU4")

    @Slot()
    def save_config(self):
        """Saves all the currently filled out information to a directory.

        This method first applies all the present (filled out in various GUI fields) information by saving them
        to the runtime config files and them copies these files to the directory specified in the config directory
        field.
        """
        try:
            self.ui.pathsbutton.click()
            self.ui.mibbutton.click()
            self.ui.prebutton.click()
            temp.evom_conf(self.ui.configfield.text())
            warn.raises("CGU5")
        except:
            warn.raises("EGU5")

    @Slot()
    def mib_use(self):
        """Use the config settings for mib tables generation.

        This method saves the config setting for mib tables generation (filled out in the GUI input field) by copying
        them to the runtime config files.
        """
        try:
            gm.update_json("mib", self.ui.mibfield.toPlainText())
            warn.raises("CGU3")
        except:
            warn.raises("EGU3")

    @Slot()
    def pre_set(self):
        """Use the config settings for pre-processor parsing.

        This method saves the config setting for per-processor parsing (filled out in the GUI input field) by copying
        them to the runtime config files.
        """
        try:
            gm.update_json("def", self.ui.prefield.toPlainText())
            warn.raises("CGU3")
        except:
            warn.raises("EGU3")

    def dist_paths(self, dic):
        """Distribute input/output paths across various GUI fields.

        This method takes the paths specified in the passed dictionary and based on their keys, assigns them to appropriate
        input text across the GUI.
        """
        if "TmHeader" in dic.keys():
            self.ui.TmHfield.setText(dic["TmHeader"])
        if "TcTmHeader" in dic.keys():
            self.ui.TcTmHfield.setText(dic["TcTmHeader"])
        if "TmFile" in dic.keys():
            self.ui.TmCfield.setText(dic["TmFile"])
        if "TcHeader" in dic.keys():
            self.ui.TcHfield.setText(dic["TcHeader"])
        if "OutDir" in dic.keys():
            self.ui.outdirfield.setText(dic["OutDir"])
        if "OutDoc" in dic.keys():
            self.ui.outdocfield.setText(dic["OutDoc"])


def gui_run():
    """Run the GUI.

    This method runs the GUI as a Qt application, which means that it is "self-contained" and upon closing it also ends
    the thread in which it was run (hence multiprocessing has to be used in order to run it as part of some larger program).
    """
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    gui_run()
