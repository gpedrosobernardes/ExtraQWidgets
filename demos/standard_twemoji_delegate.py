import sys

from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
)
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QMainWindow,
    QWidget, QHBoxLayout,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emoji Delegate com EmojiFinder")
        self.resize(520, 300)

        widget = QWidget()

        layout = QHBoxLayout()

        view = QListView()
        model = QStandardItemModel(view)

        itens = [
            "Mistura de unicode 🚀 e alias :rocket:",
            "Emoji composto: 👨‍👩‍👧‍👦 (Família)"
        ]

        for t in itens:
            model.appendRow(QStandardItem(t))

        view.setModel(model)
        view.setItemDelegate(EmojiDelegate(view))

        layout.addWidget(view)

        view_2 = QListView()
        model_2 = QStandardItemModel(view_2)

        itens_2 = [
            "Mistura de unicode 🚀 e alias :rocket:",
            "Emoji composto: 👨‍👩‍👧‍👦 (Família)"
        ]

        for t in itens_2:
            item = QStandardItem(t)
            # print(content)
            model_2.appendRow(item)

        view_2.setModel(model)

        layout.addWidget(view_2)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
