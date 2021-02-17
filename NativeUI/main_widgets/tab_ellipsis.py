from PySide2 import QtWidgets


class TabEllipsis(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabEllipsis, self).__init__(*args, **kwargs)

        grid = QtWidgets.QGridLayout()

        self.sixtyButton = QtWidgets.QPushButton("60s")
        grid.addWidget(self.sixtyButton, 0, 0)
        self.thirtyButton = QtWidgets.QPushButton("30s")
        grid.addWidget(self.thirtyButton, 0, 1)
        self.fifteenButton = QtWidgets.QPushButton("15s")
        grid.addWidget(self.fifteenButton, 1, 0)
        self.fiveButton = QtWidgets.QPushButton("5s")
        grid.addWidget(self.fiveButton, 1, 1)

        self.setLayout(grid)
