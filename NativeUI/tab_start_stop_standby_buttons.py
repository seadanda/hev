from PySide2 import QtWidgets


class TabStartStopStandbyButtons(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TabStartStopStandbyButtons, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self.button_start = QtWidgets.QPushButton()
        self.button_stop = QtWidgets.QPushButton()
        self.button_standby = QtWidgets.QPushButton()

        self.__buttons = [self.button_start, self.button_stop, self.button_standby]
        self.__buttontext = ["START", "STOP", "STANDBY"]

        for button, text in zip(self.__buttons, self.__buttontext):
            button.setText(text)
            layout.addWidget(button)

        self.setLayout(layout)
