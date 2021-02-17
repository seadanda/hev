from PySide2 import QtWidgets, QtGui, QtCore


class selectorButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(selectorButton, self).__init__(*args, **kwargs)
        style = """QPushButton{
            font:20pt;
            }
            QPushButton[selected="0"]{
            font:black;
            background-color:white ;
            border:none;
            }
            QPushButton[selected="1"]{
            font:white;
            background-color:black;
            border:none;
            }"""  # border:none is necessary to enact bg colour change

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
