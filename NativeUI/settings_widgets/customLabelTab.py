from PySide2 import QtWidgets, QtGui, QtCore
import sys


class simpleSpin(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(simpleSpin, self).__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout()

        textStyle = "color:white; font: 16pt"

        self.nameLabel = QtWidgets.QLabel("Calibration")
        self.nameLabel.setStyleSheet(textStyle)
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(self.nameLabel)

        self.simpleSpin = QtWidgets.QSpinBox()
        # self.simpleSpin.setStyleSheet("""QSpinBox{background-color:white}
        #                               QSpinBox::up-button{backgroudfnd-color:white}
        #                              QSpinBox::down-button{backgroudfnd-color:white}
        #                             """)
        self.simpleSpin.setStyleSheet(
            """QSpinBox{background-color:white; width:100px; font:16pt}
                                        QSpinBox[colour="0"]{color:black}
                                        QSpinBox[colour="1"]{color:red}
                                        QSpinBox::up-button{width:20; }
                                        QSpinBox::down-button{width:20; }
                                        """
        )
        self.simpleSpin.setProperty("colour", "1")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.simpleSpin)

        self.unitLabel = QtWidgets.QLabel("ms")
        self.unitLabel.setStyleSheet(textStyle)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.unitLabel)

        self.setLayout(layout)


class labelTab(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(labelTab, self).__init__(*args, **kwargs)

        grid = QtWidgets.QGridLayout()

        self.titleLabel = QtWidgets.QLabel("Buffers")
        self.titleLabel.setStyleSheet("background-color:white")
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.titleLabel, 0, 0, 1, 3)

        self.calibWidg = simpleSpin()
        grid.addWidget(self.calibWidg, 1, 0)

        self.purgeWidg = simpleSpin()
        grid.addWidget(self.purgeWidg, 1, 1)

        self.flushWidg = simpleSpin()
        grid.addWidget(self.flushWidg, 1, 2)

        self.preFillWidg = simpleSpin()
        grid.addWidget(self.preFillWidg, 2, 0)

        self.setLayout(grid)
