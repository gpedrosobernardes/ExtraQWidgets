from PySide6.QtGui import QStandardItem
from extra_qwidgets.widgets.theme_responsive import ThemeResponsive


class QThemeResponsiveStandardItem(QStandardItem, ThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_theme_change()