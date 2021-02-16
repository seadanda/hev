from PySide2 import QtWidgets
from PySide2.QtCore import QSize, Signal, Slot


class TabHistoryButtons(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.__button_size = QSize(50, 50)
        self.__button_font_size = 20

        self.button_sixty = HistoryButton("60s", signal_value=60)
        self.button_thirty = HistoryButton("30s", signal_value=30)
        self.button_fifteen = HistoryButton("15s", signal_value=15)
        self.button_five = HistoryButton("5s", signal_value=5)
        self.buttons = [
            self.button_sixty,
            self.button_thirty,
            self.button_fifteen,
            self.button_five,
        ]

        # Button Appearance
        for button in self.buttons:
            button.setStyleSheet(
                "QPushButton{"
                "background-color: " + NativeUI.colors["background"].name() + ";"
                "border-color: " + NativeUI.colors["background"].name() + ";"
                "color: " + NativeUI.colors["foreground"].name() + ";"
                "font-size: " + str(self.__button_font_size) + "px;"
                "}"
                "QPushButton:disabled{"
                "background-color: "
                + NativeUI.colors["background-disabled"].name()
                + ";"
                "}"
            )
            button.setFixedSize(self.__button_size)

        # Button Layout
        grid = QtWidgets.QGridLayout()
        grid_columns = 2
        i_col = 0
        i_row = 0
        for widget in self.buttons:
            grid.addWidget(widget, i_row, i_col)
            i_col += 1
            if i_col == grid_columns:
                i_col = 0
                i_row += 1

        self.setLayout(grid)

        self.button_sixty.on_press()


class HistoryButton(QtWidgets.QPushButton):
    """
    Identical to QPushButton but accepts an aditional optional argument signal_value
    that is emitted as part of the signal 'HistoryButtonPressed'. When pressed, all
    linked buttons as defined by the buttons list of the parent widget are enabled,
    while the pushed button is disabled.
    """

    HistoryButtonPressed = Signal(int)

    def __init__(self, *args, signal_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__signal_value = signal_value
        self.pressed.connect(self.on_press)

    def on_press(self):
        """
        when pressed enable all linked buttons and disable this button, then emit the
        HistoryButtonPressed signal.
        """
        try:
            _ = self.parent().buttons
        except AttributeError:
            raise Exception(
                "HistoryButton could not find parent().buttons list. You may want to be using a QPushButton instead."
            )

        for button in self.parent().buttons:
            if button != self:
                button.setEnabled(True)

        self.setEnabled(False)
        self.HistoryButtonPressed.emit(self.__signal_value)
