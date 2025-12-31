from PySide6.QtWidgets import QPushButton
from extra_qwidgets.widgets.theme_responsive import ThemeResponsive


class QThemeResponsiveButton(QPushButton, ThemeResponsive):
    def __init__(self, *args, **kwargs):
        """
        A QPushButton that changes its icon color based on the current theme.
        :param args: QPushButton's arguments
        :param kwargs: QPushButton's keyword arguments
        """
        super().__init__(*args, **kwargs)
        self._bind_theme_change()