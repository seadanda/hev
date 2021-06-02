"""
New version of what was template_main_pages.
"""
from PySide2 import QtWidgets
from PySide2.QtGui import QFont


class SwitchableStackWidget(QtWidgets.QWidget):
    def __init__(
        self, colors, text, widget_list: list, button_label_keys: list, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.widget_list = widget_list
        self.button_list = self.__make_buttons(colors, text, button_label_keys)
        self.__build()
        if len(self.button_list) > 0:
            self.setTab(self.button_list[0])

    def rebuild(self, colors, text, widget_list, button_label_keys):
        """
        For an already created SwitchableStackWidget, change the tabs in the stack.
        """
        self.__clear()
        self.widget_list = widget_list
        self.button_list = self.__make_buttons(colors, text, button_label_keys)
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

    def __make_buttons(self, colors, text, button_label_keys: list) -> list:
        """
        Make the selector buttons
        """
        return [
            SelectorButtonWidget(colors, text, label_key)
            for label_key in button_label_keys
        ]

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

    def localise_text(self, text: dict) -> int:
        for button in self.button_list:
            button.localise_text(text)
        return 0


class SelectorButtonWidget(QtWidgets.QPushButton):
    def __init__(self, colors: dict, text: dict, label_key: str, *args, **kwargs):
        super().__init__(text[label_key], *args, **kwargs)

        self.__label_key = label_key

        style = (
            "QPushButton[selected='0']{"
            "   color: " + colors["button_foreground_enabled"].name() + ";"
            "   background-color: " + colors["button_background_enabled"].name() + ";"
            "   border:none"
            "}"
            "QPushButton[selected='1']{"
            "   color: " + colors["button_foreground_highlight"].name() + ";"
            "   background-color:" + colors["button_background_highlight"].name() + ";"
            "   border:none"
            "}"
            "QPushButton:disabled{"
            "   color:" + colors["button_foreground_disabled"].name() + ";"
            "   background-color:" + colors["button_background_disabled"].name() + ";"
            "   border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")

    def localise_text(self, text: dict) -> int:
        self.setText(text[self.__label_key])
        return 0
