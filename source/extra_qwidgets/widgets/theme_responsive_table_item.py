from PySide6.QtWidgets import QTableWidgetItem
from extra_qwidgets.widgets.theme_responsive import ThemeResponsive


class QThemeResponsiveTableItem(QTableWidgetItem, ThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_theme_change()