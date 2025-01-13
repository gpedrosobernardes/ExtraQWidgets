from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QGridLayout


class QEmojiPicker(QWidget):
    def __init__(self):
        super().__init__()

        self.__line_edit = QLineEdit()
        self.__line_edit.setPlaceholderText("Enter your favorite emoji")

        self.__grid_layout = QGridLayout()

        self.__current_emoji_label = QLabel()

        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addLayout(self.__grid_layout)
        self.__horizontal_layout.addWidget(self.__current_emoji_label)

        self.setLayout(self.__horizontal_layout)

