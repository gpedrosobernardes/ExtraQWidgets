from extra_qwidgets.widgets.theme_responsive import ThemeResponsive
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QThemeResponsiveCheckButton(QThemeResponsiveButton, ThemeResponsive):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self._bind_theme_change()