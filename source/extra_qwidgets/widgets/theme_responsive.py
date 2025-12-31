from PySide6.QtWidgets import QApplication

from extra_qwidgets.utils import colorize_icon_by_theme


class ThemeResponsive:
    def _bind_theme_change(self):
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)

    def _on_theme_change(self):
        if hasattr(self, "icon") and hasattr(self, "setIcon"):
            self.setIcon(colorize_icon_by_theme(self.icon()))
