"""
New version of what was template_main_pages.
"""
from PySide2 import QtWidgets


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


class SelectorButtonWidget(QtWidgets.QPushButton):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        style = (
            "QPushButton{"
            "   font-size: " + NativeUI.text_size + ";"
            "}"
            "QPushButton[selected='0']{"
            "   font-size: " + NativeUI.text_size + ";"
            "   color: " + NativeUI.colors["page_foreground"].name() + ";"
            "   background-color: " + NativeUI.colors["background_enabled"].name() + ";"
            "   border:none"
            "}"
            "QPushButton[selected='1']{"
            "   font-size: " + NativeUI.text_size + ";"
            "   color: " + NativeUI.colors["page_background"].name() + ";"
            "   background-color:" + NativeUI.colors["foreground_disabled"].name() + ";"
            "   border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
