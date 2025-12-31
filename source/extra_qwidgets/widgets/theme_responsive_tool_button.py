from PySide6.QtWidgets import QToolButton
from extra_qwidgets.widgets.theme_responsive import ThemeResponsive


class QThemeResponsiveToolButton(QToolButton, ThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_theme_change()