import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox

from source.extra_qwidgets.widgets import QCheckBoxGroup
from source.extra_qwidgets.utils import get_awesome_icon, colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Checkbox Group Test")
        self.setWindowIcon(colorize_icon_by_theme(get_awesome_icon("python", "brands")))

        widget = QCheckBoxGroup(QLabel("Select a color:"))
        widget.add_checkbox(QCheckBox("Red"))
        widget.add_checkbox(QCheckBox("Green"))
        widget.add_checkbox(QCheckBox("Blue"))

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())