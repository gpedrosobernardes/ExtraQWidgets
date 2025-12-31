import sys

import qtawesome
from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget

from extra_qwidgets.widgets.password import QPassword
from source.extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Example")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        widget = QPassword()

        layout = QHBoxLayout()

        layout.addWidget(widget)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())