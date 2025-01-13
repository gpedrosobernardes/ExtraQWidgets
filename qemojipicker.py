from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QGridLayout, QVBoxLayout, QPushButton


class QEmojiPicker(QWidget):
    def __init__(self):
        super().__init__()

        self.__line_edit = QLineEdit()
        self.__line_edit.setPlaceholderText("Enter your favorite emoji")

        self.__grid_layout = QGridLayout()

        self.__current_emoji_label = QLabel()

        self.__menu_horizontal_layout = QHBoxLayout()

        for icon in ["face-smile", "leaf", "bowl-food", "gamepad", "bicycle", "lightbulb", "heart", "flag"]:
            button = QPushButton()
            button.setIcon(QIcon(f"assets/icons/{icon}-solid.svg"))
            self.__menu_horizontal_layout.addWidget(button)

        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addLayout(self.__grid_layout)
        self.__horizontal_layout.addWidget(self.__current_emoji_label)

        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addLayout(self.__horizontal_layout)

        self.setLayout(self.__vertical_layout)

