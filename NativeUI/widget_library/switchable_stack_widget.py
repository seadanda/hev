"""
New version of what was template_main_pages.
"""
from PySide2 import QtWidgets
from PySide2.QtGui import QFont


class SwitchableStackWidget(QtWidgets.QWidget):
    def __init__(
        self, NativeUI, widget_list: list, button_labels: list, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        self.widget_list = widget_list
        self.button_list = self.__make_buttons(button_labels)
        self.__build()
        if len(self.button_list) > 0:
            self.setTab(self.button_list[0])

    def rebuild(self, widget_list, button_labels):
        """
        For an already created SwitchableStackWidget, change the tabs in the stack.
        """
        self.__clear()
        self.widget_list = widget_list
        self.button_list = self.__make_buttons(button_labels)
        self.__build()
        self.setTab(self.button_list[0])
        return 0

    def __clear(self):
        """
        Delete all widgets in the current layout
        """
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        return 0

    def __build(self):
        """
        Construct the widget for the current status of widget_list and button_list
        """
        vlayout = QtWidgets.QVBoxLayout()
        hButtonLayout = QtWidgets.QHBoxLayout()
        self.stack = QtWidgets.QStackedWidget()

        assert len(self.widget_list) == len(self.button_list)

        for button, widget in zip(self.button_list, self.widget_list):
            hButtonLayout.addWidget(button)
            self.stack.addWidget(widget)
            button.pressed.connect(lambda i=button: self.setTab(i))

        vlayout.addLayout(hButtonLayout)
        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)

    def __make_buttons(self, button_labels: list) -> list:
        """
        Make the selector buttons
        """
        return [SelectorButtonWidget(self.NativeUI, label) for label in button_labels]

    def setTab(self, button_pressed) -> int:
        """
        Show the specified tab
        """
        for button, widget in zip(self.button_list, self.widget_list):
            if button == button_pressed:
                button.setProperty("selected", "1")
                self.stack.setCurrentWidget(widget)
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
        return 0

    def addTab(self, widget, label: str) -> int:
        """
        Add a tab to the stack
        """
        self.__clear()
        self.widget_list.append(widget)
        self.button_list += self.__make_buttons([label])
        self.__build()
        self.setTab(self.button_list[0])
        return 0

    def setFont(self, font: QFont) -> int:
        for button in self.button_list:
            button.setFont(font)

    def setButtonSize(self, x: int, y: int, spacing: int = 10) -> int:
        if x is not None and y is not None:
            for button in self.button_list:
                button.setFixedSize(x - spacing, y)
        elif x is not None and y is None:
            for button in self.button_list:
                button.setFixedWidth(x - spacing)
        elif x is None and y is not None:
            for button in self.button_list:
                button.setFixedHeight(y)
        else:
            raise AttributeError("setButtonSize called without usable size information")
        return 0


class SelectorButtonWidget(QtWidgets.QPushButton):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        style = (
            "QPushButton[selected='0']{"
            "   color: " + NativeUI.colors["button_foreground_enabled"].name() + ";"
            "   background-color: "
            + NativeUI.colors["button_background_enabled"].name()
            + ";"
            "   border:none"
            "}"
            "QPushButton[selected='1']{"
            "   color: " + NativeUI.colors["button_foreground_disabled"].name() + ";"
            "   background-color:"
            + NativeUI.colors["button_background_disabled"].name()
            + ";"
            "   border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
