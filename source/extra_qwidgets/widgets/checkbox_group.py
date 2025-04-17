import typing
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox


class QCheckBoxGroup:
    def __init__(self):
        """
        A group of checkboxes that only allows one checkbox to be checked at a time. Allows unchecking all checkboxes.
        """
        super().__init__()
        self.__checkboxes: typing.List[QCheckBox] = []
        self.__current: typing.Optional[QCheckBox] = None

    def add_checkbox(self, checkbox: QCheckBox):
        """
        Adds a checkbox to the group.
        :param checkbox: QCheckBox
        :return: None
        """
        on_check = partial(self.__on_check, checkbox)
        checkbox.checkStateChanged.connect(on_check)
        self.__checkboxes.append(checkbox)

    def add_checkboxes(self, *checkboxes: QCheckBox):
        """
        Adds multiple checkboxes to the group.
        :param checkboxes: typing.Tuple[QCheckBox]
        :return: None
        """
        for c in checkboxes:
            self.add_checkbox(c)

    def remove_checkbox(self, checkbox: QCheckBox):
        """
        Removes a checkbox from the group.
        :param checkbox: QCheckBox
        :return: None
        """
        if checkbox in self.__checkboxes:
            self.__checkboxes.remove(checkbox)

    def remove_checkboxes(self, *checkboxes: QCheckBox):
        """
        Removes multiple checkboxes from the group.
        :param checkboxes: typing.Tuple[QCheckBox]
        :return: None
        """
        for c in checkboxes:
            self.remove_checkbox(c)

    def __on_check(self, checkbox: QCheckBox, check_state: int):
        """
        Callback for when a checkbox is checked. Unchecks all other checkboxes.
        :param checkbox: QCheckBox
        :param check_state: Qt.CheckState
        :return: None
        """
        if check_state == Qt.CheckState.Checked:
            self.__current = checkbox
            for c in self.__checkboxes:
                c.setChecked(c == checkbox)
        elif checkbox == self.__current:
            self.__current = None

    def get_checked(self) -> typing.Optional[QCheckBox]:
        """
        Returns the currently checked checkbox.
        :return: typing.Optional[QCheckBox]
        """
        return self.__current

    def get_checked_name(self) -> typing.Optional[str]:
        """
        Returns the object name of the currently checked checkbox.
        :return: typing.Optional[str]
        """
        return self.__current.objectName() if self.__current is not None else None

    def checkboxes(self) -> typing.List[QCheckBox]:
        """
        Returns all checkboxes in the group.
        :return: typing.List[QCheckBox]
        """
        return self.__checkboxes

    def reset(self):
        """
        Resets the checkboxes.
        :return: None
        """
        for c in self.__checkboxes:
            c.setChecked(False)

    def check_by_name(self, name: str) -> typing.Optional[QCheckBox]:
        """
        Checks the checkbox with the given name. Returns the object of the checkbox if found.
        :param name: str
        :return: typing.Optional[QCheckBox]
        """
        for c in self.__checkboxes:
            if c.objectName() == name:
                c.setChecked(True)
                return c
        return None