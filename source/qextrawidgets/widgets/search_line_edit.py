from PySide6.QtWidgets import QLineEdit

from qextrawidgets.icons import QThemeResponsiveIcon


class QSearchLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setClearButtonEnabled(True)
        self.addAction(QThemeResponsiveIcon.fromAwesome("fa6s.magnifying-glass"), QLineEdit.ActionPosition.LeadingPosition)