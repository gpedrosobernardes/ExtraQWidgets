import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QVBoxLayout

from qemojipicker import QEmojiPicker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emoji Picker Test")

        widget = QWidget()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter your favorite emoji")
        emoji_picker = QEmojiPicker()

        # center line_edit on widget
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(emoji_picker)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
