import typing

from PySide6.QtWidgets import QGridLayout, QWidget, QLabel, QCheckBox

from extra_qwidgets.widgets import QCheckBoxGroup


class QCheckBoxes(QWidget):
    def __init__(self, label: QLabel):
        """
        A widget group of checkboxes with a label.
        :param label: QLabel
        """
        super().__init__()
        self.__layout = QGridLayout()
        self.__label = label
        self.__checkbox_group = QCheckBoxGroup()
        self.__layout.addWidget(self.__label, 0, 0)
        self.setLayout(self.__layout)

    def add_checkbox(self, checkbox: QCheckBox):
        """
        Adds a checkbox to the widget.
        :param checkbox: QCheckBox
        :return: None
        """
        self.__layout.addWidget(checkbox, len(self.checkboxes()), 1)
        self.__checkbox_group.add_checkbox(checkbox)

    def add_checkboxes(self, *checkboxes: QCheckBox):
        """
        Adds multiple checkboxes to the widget.
        :param checkboxes: typing.Tuple[QCheckBox]
        :return: None
        """
        for c in checkboxes:
            self.add_checkbox(c)

    def remove_checkbox(self, checkbox: QCheckBox):
        """
        Removes a checkbox from the widget.
        :param checkbox: QCheckBox
        :return: None
        """
        self.__layout.removeWidget(checkbox)
        self.__checkbox_group.remove_checkbox(checkbox)

    def remove_checkboxes(self, *checkboxes: QCheckBox):
        """
        Removes multiple checkboxes from the widget.
        :param checkboxes: typing.Tuple[QCheckBox]
        :return: None
        """
        for c in checkboxes:
            self.remove_checkbox(c)

    def get_checked(self) -> QCheckBox:
        """
        Returns the currently checked checkbox.
        :return: typing.Optional[QCheckBox]
        """
        return self.__checkbox_group.get_checked()

    def get_checked_name(self) -> typing.Optional[str]:
        """
        Returns the object name of the currently checked checkbox.
        :return: typing.Optional[str]
        """
        return self.__checkbox_group.get_checked_name()

    def checkboxes(self) -> typing.List[QCheckBox]:
        """
        Returns all checkboxes in the widget.
        :return: typing.List[QCheckBox]
        """
        return self.__checkbox_group.checkboxes()