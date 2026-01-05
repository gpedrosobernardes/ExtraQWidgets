import sys

from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem, Qt,
)
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QMainWindow,
    QWidget, QHBoxLayout,
)

from qextrawidgets.delegates.standard_twemoji_delegate import QStandardTwemojiDelegate
from qextrawidgets.icons import QThemeResponsiveIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QStandardTwemojiDelegate Demo")
        self.resize(520, 300)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QWidget()

        layout = QHBoxLayout()

        view = QListView()
        model = QStandardItemModel(view)

        itens = [
            "Mistura de unicode 🚀 e alias :rocket:",
            "Emoji composto: 👨‍👩‍👧‍👦 (Família)"
        ]

        for t in itens:
            item = QStandardItem(t)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            model.appendRow(item)


        view.setModel(model)
        delegate = QStandardTwemojiDelegate(view)
        view.setItemDelegate(delegate)

        layout.addWidget(view)

        view_2 = QListView()
        view_2.setMouseTracking(True)
        model_2 = QStandardItemModel(view_2)

        itens_2 = [
            "Mistura de unicode 🚀 e alias :rocket:",
            "Emoji composto: 👨‍👩‍👧‍👦 (Família)"
        ]

        for t in itens_2:
            item = QStandardItem(t)
            # print(content)

            model_2.appendRow(item)

        view_2.setModel(model_2)

        layout.addWidget(view_2)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
