import qtawesome
from PySide6.QtWidgets import QListWidget, QAbstractButton

from extra_qwidgets.abstract.single_selection_list import AbstractSingleSelectionList
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QSingleSelectionList(AbstractSingleSelectionList):
    def _new_tool_button(self, icon: str) -> QAbstractButton:
        tool_button = QThemeResponsiveButton()
        tool_button.setFlat(True)
        tool_button.setIcon(qtawesome.icon(icon))
        return tool_button

    def _new_list_widget(self) -> QListWidget:
        return QListWidget()