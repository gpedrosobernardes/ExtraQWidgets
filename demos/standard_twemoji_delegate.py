import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from qextrawidgets.delegates.standard_twemoji_delegate import QStandardTwemojiDelegate
from qextrawidgets.icons import QThemeResponsiveIcon


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QStandardTwemojiDelegate Demo")
        self.resize(600, 400)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Description
        description = QLabel(
            "This demo showcases the <b>QStandardTwemojiDelegate</b>.<br>"
            "It supports rendering of Unicode emojis within standard item views."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # List View
        view = QListView()
        model = QStandardItemModel(view)

        # Test Data: (Text, Alignment)
        items_data = [
            ("Unicode Emoji: 🚀", Qt.AlignmentFlag.AlignLeft),
            ("Mixed: Hello World 🌍", Qt.AlignmentFlag.AlignCenter),
            ("Complex: 👨‍👩‍👧‍👦 (Family)", Qt.AlignmentFlag.AlignRight),
            ("Flags: 🇧🇷 🇯🇵", Qt.AlignmentFlag.AlignCenter),
            ("Text only (no emoji)", Qt.AlignmentFlag.AlignLeft),
            ("Multiple: 😄 ❤️ 👍", Qt.AlignmentFlag.AlignLeft),
        ]

        for text, alignment in items_data:
            item = QStandardItem(text)
            item.setTextAlignment(alignment)
            model.appendRow(item)

        view.setModel(model)

        # Apply Delegate
        delegate = QStandardTwemojiDelegate(view)
        view.setItemDelegate(delegate)

        layout.addWidget(view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
