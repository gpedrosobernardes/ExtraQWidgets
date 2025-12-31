from PySide6.QtGui import QAction
from extra_qwidgets.widgets.theme_responsive import ThemeResponsive


class QThemeResponsiveAction(QAction, ThemeResponsive):
    def __init__(self, *args, **kwargs):
        """
        A QAction that changes its icon color based on the current theme.
        :param args: QAction's arguments
        :param kwargs: QAction's keyword arguments
        """
        super().__init__(*args, **kwargs)
        self._bind_theme_change()