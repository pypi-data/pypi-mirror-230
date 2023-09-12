"""Allow a GUI representation of the parsed data.

This module allows the user to see the output of the parsing process, i.e. the tree of the Python objects that were created as
a representation of the original C-files. For the creation of the GUI the Qt framework is used in connection with its Python 
toolkit/bindings PySide-6.
"""
import multiprocessing
import sys

from PySide6.QtCore import QMetaObject
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QToolBox,
    QVBoxLayout,
    QWidget,
)

import mib_generator.data.longdata as longdata
import mib_generator.parsing.load as load

policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)


class CommentWindow(QWidget):
    """Small window that shows informations about comments in the given entry.

    This class holds a description of the UI layout of a comment window that is shown when the user asks to view contents of
    some comment. Apart from passively showing all the entries, it can also call other window when the user asks to view full
    text of some comment.

    Args:
        comment (list): List of comments to be shown in the window. Each of type :obj:`parsing.par_methods.comment`.
    """

    def __init__(self, comment):
        super().__init__()
        self.setWindowTitle("Comment view")
        # self.resize(600,500)
        layout = QVBoxLayout()
        for i in comment:
            label = QLabel("Comment:")
            layout.addWidget(label)
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            lay = QVBoxLayout(frame)
            button = QPushButton("Show full text", frame)
            button.clicked.connect(lambda: self.view_text(i.text))
            lay.addWidget(button)
            labeli = QLabel(frame)
            labeli.setText("Basic information:")
            lay.addWidget(labeli)
            table = QTableWidget(frame)
            intable(table, getdata(i))
            lay.addWidget(table)
            labe = QLabel(frame)
            labe.setText("Entries:")
            lay.addWidget(labe)
            table2 = QTableWidget(frame)
            intable(table2, list(i.entries.items()))
            lay.addWidget(table2)
            layout.addWidget(frame)
        self.setLayout(layout)

    def view_text(self, text):
        """Show a window with full text.

        This methods when called opens a small window showing the passed text.

        Args:
            text (str): The text to be shown.
        """
        self.b = TextWindow(text)
        self.b.show()


class TextWindow(QWidget):
    """Small window that show parsed text.

    This class holds description of an UI layout of a small window that can display a single block of text.
    It is created mostly in cases when contents of some longer entry or section of C-file have to be shown.
    """

    def __init__(self, text):
        super().__init__()
        self.setWindowTitle("Full text view")
        layout = QVBoxLayout()
        textpol = QPlainTextEdit(text)
        textpol.setFrameShape(QFrame.NoFrame)
        textpol.setReadOnly(True)
        layout.addWidget(textpol)
        self.setLayout(layout)


class Ui_MainWindow(object):
    """This class holds functions that build up geometry and objects in the main window.

    In case of this application, the UI has to be dynamically created, i.e. the number of entries in a toolbox has to change
    depending on the number of structures that need to be displayed. Because of this, this class which holds the description
    of the UI of the main visualisation window is perhaps more complicated than usual. Its base layout is created in
    :obj:`setupUi`, but this includes a recursive reference to :obj:`inter`, which always creates a visualisation of contents
    of some object (i.e. shows a list of some objects as entries in a toolbox). Since structures can be members of
    structures, :obj:`inter` can also call itself, hence the recursivity.
    """

    def setupUi(self, MainWindow, struct):
        """Builds up the UI of the Main window.

        This is done dynamically based on the nature of the passed file representation. See :obj:`Ui_MainWindow` for more info.

        Args:
            MainWindow (QMainWindow): Base Qt object in which this UI is build.
            struct (parsing.parser_main.file): The Python representation of a file on basis of which the UI will be constructed.
        """
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        centralwidget = QWidget(MainWindow)
        verlay = QVBoxLayout(centralwidget)
        scrolarea = QScrollArea(centralwidget)
        scrolarea.setWidgetResizable(True)
        widget = self.inter(struct)
        widget.setSizePolicy(policy)
        scrolarea.setWidget(widget)
        verlay.addWidget(scrolarea)
        MainWindow.setCentralWidget(centralwidget)

        # self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def inter(self, struct):
        """Recursively create entries for each C-object in the parsed file.

        For any passed parsed object, creates an appropriate representation through a Qt Widget. Since such object can also
        be a ``struct``, this function is sometimes called recursively. For some objects it also creates buttons which can open
        other windows which visualise associated comments or e.g. long section of the original C-file.

        Args:
            struct (child-class of parsing.par_header.structure or parsing.par_cfile.instance_og): The object to be visualised
                by the custom-created Qt Widget.

        Returns:
            QFrame: Qt widget representing the passed object.
        """
        page = QFrame()
        page.setFrameShape(QFrame.Box)
        page.setSizePolicy(policy)
        verlay = QVBoxLayout(page)
        methods = struct.__dir__()
        if "structures" in methods:
            toolbox = QToolBox(page)
            for i in struct.structures:
                subwid = self.inter(i)
                toolbox.addItem(subwid, i.text.replace("\n", "\\n")[:50] + "...")
            verlay.addWidget(toolbox)
        else:
            buttont = QPushButton("Show full text", page)
            buttont.clicked.connect(lambda: self.view_text(struct.text))
            verlay.addWidget(buttont)
        if "type" in methods:
            labeli = QLabel(page)
            labeli.setText("Extracted information:")
            verlay.addWidget(labeli)
            data = getdata(struct)
            table = QTableWidget(page)
            intable(table, data)
            verlay.addWidget(table)
        if "comment" in methods and len(struct.comment) > 0:
            button = QPushButton("View comments", page)
            # I cannot believe this works
            button.clicked.connect(lambda: self.view_comments(struct.comment))
            verlay.addWidget(button)
        if "entries" in methods:
            label2 = QLabel(page)
            label2.setText("Entries:")
            verlay.addWidget(label2)
            table2 = QTableWidget(page)
            intable(table2, list(struct.entries.items()))
            verlay.addWidget(table2)
        if "elements" in methods:
            label = QLabel(page)
            label.setText("Objects inside:")
            verlay.addWidget(label)
            toolbox = QToolBox(page)
            for i in struct.elements:
                subwid = self.inter(i)
                toolbox.addItem(subwid, i.text.replace("\n", "\\n"))
            verlay.addWidget(toolbox)
        if "form" in methods and type(struct.form) is not str:
            label3 = QLabel(page)
            label3.setText("In this structure:")
            verlay.addWidget(label3)
            subview = self.inter(struct.form)
            subview.setParent(page)
            verlay.addWidget(subview)

        return page

    def view_comments(self, comment):
        """Show a window with comments.

        This method when called opens a window showing the passed comment.

        Args:
            comment (list): List of comments to be shown in the new window. Each of
                type :obj:`mib_generator.parsing.par_methods.comment`.
        """
        self.a = CommentWindow(comment)
        self.a.show()

    def view_text(self, text):
        """Show a window with full text.

        This method when called opens a small window showing the passed text.

        Args:
            text (str): The text to be shown.
        """
        self.b = TextWindow(text)
        self.b.show()


def getdata(struct):
    """Extract all posible showable (str, int) data about an object

    From a list of attributes that the passed object has, extracts the interesting ones (which are not buildins for any Python
    object) and if they have showable value (their value is either ``str`` or ``int`` and it isn't the whole text of the
    corresponding C code found in the original C-file), adds this attribute-value pair to a list. It also tries to substitute
    the name of the attribute with a more human-readable name by looking it up in
    :obj:`mib_generator.data.longdata.translation`.

    Args:
        struct (any Python object really): The object who's attributes are to be extracted.

    Returns:
        list: A list holding all "interesting" attributes of the original object jointly with their values.
    """
    data = []
    dic = struct.__dict__
    for i in dic:
        if (type(dic[i]) is str or type(dic[i]) is int) and i != "text":
            try:
                data.append([longdata.translation[i], dic[i]])
            except KeyError:
                data.append([i + ":", dic[i]])
    return data


def intable(table, data):
    """Add the given data to the given table.

    This method takes a table (its representation as a Qt widget) and inputs the passed data into its rows and columns.
    It expects the inputted data to be a list of pairs.

    Args:
        table (QTableWidget): The Qt table to which the data is to be added.
        data (list): List of pairs representing the data to be added to the table.
    """
    table.setColumnCount(2)
    table.setRowCount(len(data))
    for i in range(len(data)):
        e1 = QTableWidgetItem(data[i][0])
        e2 = QTableWidgetItem(str(data[i][1]))
        table.setItem(i, 0, e1)
        table.setItem(i, 1, e2)
        table.resizeColumnToContents(0)
        table.resizeColumnToContents(1)
    table.horizontalHeader().setVisible(False)
    table.verticalHeader().setVisible(False)
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)


class MainWindow(QMainWindow):
    """The class of the main window.

    This class is the actual Qt representation of the Main Window with all of its aspects. Since the whole UI is generated
    in :obj:`Ui_MainWindow`, not much happens here.

    Args:
        struct (parsing.parser_main.file): The Python representation of the file on basis of which the UI will be constructed.
    """

    def __init__(self, struct):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, struct)
        self.setWindowTitle("Structure viewer - " + str(struct.path))


def runt(struct):
    """Run the app in one process.

    This method first creates the UI based on the passed file representation and then runs it as a Qt app.

    At the exit, this method kills the whole process so it should be isolated into separate process if it is only called by
    some additional code which is supposed to continue running.

    Args:
        struct (parsing.parser_main.file): The Python representation of the file on basis of which the visualisation will
            be constructed.
    """
    app = QApplication(sys.argv)
    window = MainWindow(struct)
    window.show()
    sys.exit(app.exec())


def main(struct=[load.TmH]):
    """For each file create a process and run the visualiser in it.

    This method creates (or rather starts the process of creating) a visualisation window for each of the files in the passed
    list. In order to do this it has to create a separate new process for each of the files since otherwise closing the windows
    would exit the whole Python runtime.
    """
    for i in struct:
        t = multiprocessing.Process(target=runt, args=[i])
        t.start()
