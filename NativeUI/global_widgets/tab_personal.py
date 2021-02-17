from PySide2 import QtGui, QtWidgets, QtCore


class TabPersonal(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabPersonal, self).__init__(*args, **kwargs)

        self.infoLabel = QtWidgets.QLabel("Person person, 55kg")
        self.infoLabel.setStyleSheet("font:15pt;color:white")
        self.infoLabel.setAlignment(QtCore.Qt.AlignCenter)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.infoLabel)
        self.setLayout(hlayout)
